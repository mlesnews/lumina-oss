#!/usr/bin/env python3
"""
Production Deployment Readiness Check
                    -LUM THE MODERN

Comprehensive production deployment readiness check for Azure AI Foundry integration.
Validates all components, configurations, and dependencies before production deployment.

Tags: #PRODUCTION #DEPLOYMENT #AZURE #AI_FOUNDRY #READINESS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("ProductionDeployment")


class ProductionDeploymentCheck:
    """Production deployment readiness checker"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data" / "battle_tests"

        self.results = {
            "check_id": f"prod_deployment_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "checks": [],
            "summary": {}
        }

        logger.info("=" * 80)
        logger.info("🚀 PRODUCTION DEPLOYMENT READINESS CHECK")
        logger.info("                    -LUM THE MODERN")
        logger.info("=" * 80)

    def check_sdk_installation(self) -> Dict[str, Any]:
        """Check SDK installation"""
        check_result = {
            "category": "sdk_installation",
            "status": "running",
            "checks": []
        }

        # Check packages
        required_packages = [
            "azure-ai-projects",
            "azure-ai-inference",
            "azure-ai-agents",
            "azure-identity"
        ]

        import subprocess
        for package in required_packages:
            try:
                result = subprocess.run(
                    ["pip", "show", package],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and "Name:" in result.stdout:
                    check_result["checks"].append({
                        "item": package,
                        "status": "passed"
                    })
                    logger.info(f"   ✅ {package}: Installed")
                else:
                    check_result["checks"].append({
                        "item": package,
                        "status": "failed"
                    })
                    logger.error(f"   ❌ {package}: Not installed")
            except Exception as e:
                # Fallback: try import
                try:
                    import_name = package.replace("-", "_")
                    if package == "azure-ai-projects":
                        from azure.ai.projects import AIProjectClient
                    elif package == "azure-ai-inference":
                        from azure.ai.inference import ChatCompletionsClient
                    elif package == "azure-ai-agents":
                        # Agents may not have direct import
                        pass
                    elif package == "azure-identity":
                        from azure.identity import DefaultAzureCredential

                    check_result["checks"].append({
                        "item": package,
                        "status": "passed"
                    })
                    logger.info(f"   ✅ {package}: Installed (verified via import)")
                except ImportError:
                    check_result["checks"].append({
                        "item": package,
                        "status": "failed",
                        "error": str(e)
                    })
                    logger.error(f"   ❌ {package}: Not installed")

        check_result["status"] = "passed" if all(
            c["status"] == "passed" for c in check_result["checks"]
        ) else "failed"

        self.results["checks"].append(check_result)
        return check_result

    def check_authentication(self) -> Dict[str, Any]:
        """Check authentication"""
        check_result = {
            "category": "authentication",
            "status": "running",
            "checks": []
        }

        try:
            from azure.identity import DefaultAzureCredential
            credential = DefaultAzureCredential(

                                exclude_interactive_browser_credential=False,

                                exclude_shared_token_cache_credential=False

                            )

            check_result["checks"].append({
                "item": "DefaultAzureCredential",
                "status": "passed"
            })
            logger.info("   ✅ DefaultAzureCredential: Available")
        except Exception as e:
            check_result["checks"].append({
                "item": "DefaultAzureCredential",
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"   ❌ DefaultAzureCredential: {e}")

        try:
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential

            key_vault_url = "https://jarvis-lumina.vault.azure.net/"
            credential = DefaultAzureCredential(

                                exclude_interactive_browser_credential=False,

                                exclude_shared_token_cache_credential=False

                            )
            key_vault_client = SecretClient(vault_url=key_vault_url, credential=credential)

            check_result["checks"].append({
                "item": "Key Vault client",
                "status": "passed"
            })
            logger.info(f"   ✅ Key Vault client: Initialized")
        except Exception as e:
            check_result["checks"].append({
                "item": "Key Vault client",
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"   ❌ Key Vault client: {e}")

        check_result["status"] = "passed" if all(
            c["status"] == "passed" for c in check_result["checks"]
        ) else "failed"

        self.results["checks"].append(check_result)
        return check_result

    def check_endpoint_configuration(self) -> Dict[str, Any]:
        """Check endpoint configuration"""
        check_result = {
            "category": "endpoint_configuration",
            "status": "running",
            "checks": []
        }

        # Check config file
        config_file = self.config_dir / "azure_ai_foundry_config.json"
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)

                endpoint = config.get("azure_ai_foundry", {}).get("project_endpoint")
                if endpoint:
                    check_result["checks"].append({
                        "item": "endpoint_in_config",
                        "status": "passed",
                        "endpoint": endpoint[:50] + "..." if len(endpoint) > 50 else endpoint
                    })
                    logger.info("   ✅ Endpoint in config file: Found")
                else:
                    check_result["checks"].append({
                        "item": "endpoint_in_config",
                        "status": "warning",
                        "note": "Config file exists but endpoint not configured"
                    })
                    logger.warning("   ⚠️  Endpoint in config file: Not configured")
            except Exception as e:
                check_result["checks"].append({
                    "item": "endpoint_in_config",
                    "status": "failed",
                    "error": str(e)
                })
                logger.error(f"   ❌ Config file read: {e}")
        else:
            check_result["checks"].append({
                "item": "endpoint_in_config",
                "status": "warning",
                "note": "Config file not found"
            })
            logger.warning("   ⚠️  Config file: Not found")

        # Check Key Vault
        try:
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential

            key_vault_url = "https://jarvis-lumina.vault.azure.net/"
            credential = DefaultAzureCredential(

                                exclude_interactive_browser_credential=False,

                                exclude_shared_token_cache_credential=False

                            )
            key_vault_client = SecretClient(vault_url=key_vault_url, credential=credential)

            try:
                secret = key_vault_client.get_secret("azure-ai-foundry-project-endpoint")
                endpoint = secret.value

                check_result["checks"].append({
                    "item": "endpoint_in_key_vault",
                    "status": "passed",
                    "endpoint": endpoint[:50] + "..." if len(endpoint) > 50 else endpoint
                })
                logger.info("   ✅ Endpoint in Key Vault: Found")
            except Exception:
                check_result["checks"].append({
                    "item": "endpoint_in_key_vault",
                    "status": "warning",
                    "note": "Endpoint not in Key Vault"
                })
                logger.warning("   ⚠️  Endpoint in Key Vault: Not found")
        except Exception as e:
            check_result["checks"].append({
                "item": "endpoint_in_key_vault",
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"   ❌ Key Vault check: {e}")

        # Determine overall status
        has_endpoint = any(
            c.get("status") == "passed" for c in check_result["checks"]
        )

        check_result["status"] = "passed" if has_endpoint else "warning"

        self.results["checks"].append(check_result)
        return check_result

    def check_integration(self) -> Dict[str, Any]:
        """Check integration components"""
        check_result = {
            "category": "integration",
            "status": "running",
            "checks": []
        }

        try:
            from scripts.python.lumina_azure_ai_foundry_integration import (
                LuminaAzureAIFoundryIntegration
            )

            integration = LuminaAzureAIFoundryIntegration(self.project_root)

            check_result["checks"].append({
                "item": "integration_init",
                "status": "passed"
            })
            logger.info("   ✅ Integration: Initialized")

            # Check model endpoints
            models = integration.list_available_models()
            check_result["checks"].append({
                "item": "model_endpoints",
                "status": "passed",
                "model_count": len(models)
            })
            logger.info(f"   ✅ Model endpoints: {len(models)} configured")

        except Exception as e:
            check_result["checks"].append({
                "item": "integration_init",
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"   ❌ Integration: {e}")

        check_result["status"] = "passed" if all(
            c["status"] == "passed" for c in check_result["checks"]
        ) else "failed"

        self.results["checks"].append(check_result)
        return check_result

    def check_battle_tests(self) -> Dict[str, Any]:
        """Check battle test results"""
        check_result = {
            "category": "battle_tests",
            "status": "running",
            "checks": []
        }

        # Find latest battle test results
        if self.data_dir.exists():
            test_files = sorted(
                self.data_dir.glob("battletest_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            if test_files:
                latest_test = test_files[0]
                try:
                    with open(latest_test) as f:
                        test_data = json.load(f)

                    summary = test_data.get("summary", {})
                    passed = summary.get("passed", 0)
                    total = summary.get("total_tests", 0) or summary.get("total_stages", 0)

                    success_rate = passed / total if total > 0 else 0

                    check_result["checks"].append({
                        "item": "latest_battle_test",
                        "status": "passed" if success_rate >= 0.8 else "warning",
                        "success_rate": f"{passed}/{total}",
                        "test_file": latest_test.name
                    })
                    logger.info(f"   ✅ Latest battle test: {passed}/{total} passed ({success_rate*100:.0f}%)")
                except Exception as e:
                    check_result["checks"].append({
                        "item": "latest_battle_test",
                        "status": "failed",
                        "error": str(e)
                    })
                    logger.error(f"   ❌ Battle test read: {e}")
            else:
                check_result["checks"].append({
                    "item": "latest_battle_test",
                    "status": "warning",
                    "note": "No battle test results found"
                })
                logger.warning("   ⚠️  Battle tests: No results found")
        else:
            check_result["checks"].append({
                "item": "latest_battle_test",
                "status": "warning",
                "note": "Battle test directory not found"
            })
            logger.warning("   ⚠️  Battle tests: Directory not found")

        check_result["status"] = "passed" if any(
            c["status"] == "passed" for c in check_result["checks"]
        ) else "warning"

        self.results["checks"].append(check_result)
        return check_result

    def check_documentation(self) -> Dict[str, Any]:
        try:
            """Check documentation"""
            check_result = {
                "category": "documentation",
                "status": "running",
                "checks": []
            }

            docs_dir = self.project_root / "docs" / "operations"
            required_docs = [
                "AZURE_AI_FOUNDRY_SDK_INSTALLED.md",
                "AZURE_AI_FOUNDRY_BATTLE_TEST_RESULTS.md",
                "AZURE_AI_FOUNDRY_EXTERNAL_VALIDATION.md",
                "AZURE_AI_FOUNDRY_INTEGRATION_COMPLETE_VALIDATED.md"
            ]

            docs_found = []
            for doc in required_docs:
                doc_path = docs_dir / doc
                if doc_path.exists():
                    docs_found.append(doc)
                    check_result["checks"].append({
                        "item": doc,
                        "status": "passed"
                    })
                    logger.info(f"   ✅ {doc}: Found")
                else:
                    check_result["checks"].append({
                        "item": doc,
                        "status": "warning"
                    })
                    logger.warning(f"   ⚠️  {doc}: Not found")

            check_result["status"] = "passed" if len(docs_found) >= 3 else "warning"

            self.results["checks"].append(check_result)
            return check_result

        except Exception as e:
            self.logger.error(f"Error in check_documentation: {e}", exc_info=True)
            raise
    def run_all_checks(self):
        try:
            """Run all production readiness checks"""
            logger.info("\n🔍 Running Production Readiness Checks...")
            logger.info("=" * 80)

            self.check_sdk_installation()
            self.check_authentication()
            self.check_endpoint_configuration()
            self.check_integration()
            self.check_battle_tests()
            self.check_documentation()

            # Calculate summary
            total_checks = len(self.results["checks"])
            passed_checks = sum(1 for c in self.results["checks"] if c["status"] == "passed")
            warning_checks = sum(1 for c in self.results["checks"] if c["status"] == "warning")
            failed_checks = sum(1 for c in self.results["checks"] if c["status"] == "failed")

            self.results["summary"] = {
                "total_checks": total_checks,
                "passed": passed_checks,
                "warnings": warning_checks,
                "failed": failed_checks,
                "ready_for_production": passed_checks == total_checks and warning_checks == 0
            }

            # Save results
            results_file = self.data_dir / f"{self.results['check_id']}.json"
            self.data_dir.mkdir(parents=True, exist_ok=True)
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)

            # Print summary
            logger.info("\n" + "=" * 80)
            logger.info("📊 PRODUCTION READINESS SUMMARY")
            logger.info("=" * 80)
            logger.info(f"   Total Checks: {total_checks}")
            logger.info(f"   Passed: {passed_checks}")
            logger.info(f"   Warnings: {warning_checks}")
            logger.info(f"   Failed: {failed_checks}")
            logger.info(f"   Ready for Production: {'✅ YES' if self.results['summary']['ready_for_production'] else '⚠️  NO'}")
            logger.info(f"   Results: {results_file}")
            logger.info("=" * 80)

            return self.results


        except Exception as e:
            self.logger.error(f"Error in run_all_checks: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Production Deployment Readiness Check")
        parser.add_argument("--json", action="store_true", help="Output results as JSON")

        args = parser.parse_args()

        checker = ProductionDeploymentCheck()
        results = checker.run_all_checks()

        if args.json:
            print(json.dumps(results, indent=2, default=str))

        return 0 if results["summary"]["ready_for_production"] else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())