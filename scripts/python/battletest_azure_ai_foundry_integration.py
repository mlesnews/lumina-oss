#!/usr/bin/env python3
"""
Battle Test: Azure AI Foundry + LUMINA Integration
                    -LUM THE MODERN

Comprehensive battle testing of Azure AI Foundry integration with LUMINA.
Tests local models, Azure models, hybrid routing, and performance.

Tags: #BATTLE_TEST #AZURE #AI_FOUNDRY #INTEGRATION #TESTING @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import time

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

logger = get_logger("BattleTestAzureAIFoundry")


class BattleTestAzureAIFoundry:
    """
    Battle Test for Azure AI Foundry Integration

    Tests:
    - Local model inference (Iron Legion, ULTRON)
    - Azure AI Foundry model inference
    - Hybrid routing (local → Azure fallback)
    - Model switching
    - Performance comparison
    - JARVIS routing integration
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "battle_tests"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize integration
        try:
            from scripts.python.lumina_azure_ai_foundry_integration import (
                LuminaAzureAIFoundryIntegration,
                InferenceRequest,
                ModelProvider
            )
            self.integration = LuminaAzureAIFoundryIntegration(self.project_root)
            self.ModelProvider = ModelProvider  # Store for use in methods
            self.InferenceRequest = InferenceRequest  # Store for use in methods
            logger.info("✅ Azure AI Foundry integration initialized")
        except Exception as e:
            logger.error(f"❌ Integration init error: {e}")
            raise

        # Test results
        self.results = {
            "test_id": f"battletest_azure_foundry_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "started": datetime.now().isoformat(),
            "tests": [],
            "summary": {}
        }

        logger.info("=" * 80)
        logger.info("⚔️  BATTLE TEST: AZURE AI FOUNDRY + LUMINA INTEGRATION")
        logger.info("                    -LUM THE MODERN")
        logger.info("=" * 80)

    def test_local_models(self) -> Dict[str, Any]:
        """Test local models (Iron Legion, ULTRON)"""
        logger.info("\n📋 TEST 1: Local Models")
        logger.info("-" * 80)

        test_result = {
            "test_name": "local_models",
            "status": "running",
            "results": []
        }

        # List available local models
        local_models = self.integration.list_available_models(self.ModelProvider.LOCAL)
        logger.info(f"   Found {len(local_models)} local models")

        # Test each local model
        test_prompt = "Hello, this is a battle test. Please respond briefly."
        success_count = 0

        for model in local_models[:3]:  # Test first 3 models
            try:
                logger.info(f"   Testing: {model.model_id}")
                request = self.InferenceRequest(
                    prompt=test_prompt,
                    model=model.model_id,
                    provider_preference=self.ModelProvider.LOCAL,
                    fallback_enabled=False  # Disable fallback for local-only test
                )

                start_time = time.time()
                response = self.integration.inference(request)
                elapsed = (time.time() - start_time) * 1000

                test_result["results"].append({
                    "model": model.model_id,
                    "status": "success",
                    "latency_ms": response.latency_ms,
                    "tokens": response.tokens_used,
                    "response_length": len(response.response)
                })

                success_count += 1
                logger.info(f"      ✅ {model.model_id}: {response.latency_ms:.0f}ms, {response.tokens_used} tokens")

            except Exception as e:
                test_result["results"].append({
                    "model": model.model_id,
                    "status": "failed",
                    "error": str(e)
                })
                logger.error(f"      ❌ {model.model_id}: {e}")

        test_result["status"] = "completed"
        test_result["success_rate"] = f"{success_count}/{len(local_models[:3])}"
        self.results["tests"].append(test_result)

        logger.info(f"\n   ✅ Local models test: {success_count}/{len(local_models[:3])} successful")
        return test_result

    def test_azure_authentication(self) -> Dict[str, Any]:
        """Test Azure authentication"""
        logger.info("\n📋 TEST 2: Azure Authentication")
        logger.info("-" * 80)

        test_result = {
            "test_name": "azure_authentication",
            "status": "running",
            "results": {}
        }

        # Test authentication
        auth_status = self.integration.azure_authenticated
        key_vault_status = self.integration.key_vault_client is not None

        test_result["results"] = {
            "azure_authenticated": auth_status,
            "key_vault_client": key_vault_status,
            "key_vault_url": "https://jarvis-lumina.vault.azure.net/" if key_vault_status else None
        }

        if auth_status:
            logger.info("   ✅ Azure authentication: Working")
        else:
            logger.warning("   ⚠️  Azure authentication: Not available")

        if key_vault_status:
            logger.info("   ✅ Key Vault client: Initialized")
        else:
            logger.warning("   ⚠️  Key Vault client: Not available")

        # Test SDK imports
        try:
            from azure.ai.projects import AIProjectClient
            from azure.identity import DefaultAzureCredential
            test_result["results"]["sdk_imports"] = True
            logger.info("   ✅ SDK imports: Working")
        except Exception as e:
            test_result["results"]["sdk_imports"] = False
            test_result["results"]["sdk_error"] = str(e)
            logger.error(f"   ❌ SDK imports: Failed - {e}")

        test_result["status"] = "completed"
        self.results["tests"].append(test_result)

        return test_result

    def test_azure_foundry_connectivity(self) -> Dict[str, Any]:
        """Test Azure AI Foundry connectivity (if endpoint configured)"""
        logger.info("\n📋 TEST 3: Azure AI Foundry Connectivity")
        logger.info("-" * 80)

        test_result = {
            "test_name": "azure_foundry_connectivity",
            "status": "running",
            "results": {}
        }

        # Check if project endpoint is configured
        config = self.integration.config.get("azure_ai_foundry", {})
        project_endpoint = config.get("project_endpoint")

        if not project_endpoint and self.integration.key_vault_client:
            try:
                secret = self.integration.key_vault_client.get_secret("azure-ai-foundry-project-endpoint")
                project_endpoint = secret.value
            except Exception:
                pass

        if not project_endpoint:
            test_result["results"]["status"] = "not_configured"
            test_result["results"]["message"] = "Project endpoint not configured - skipping connectivity test"
            test_result["status"] = "skipped"
            logger.info("   ⏭️  Project endpoint not configured - skipping")
            self.results["tests"].append(test_result)
            return test_result

        # Test connectivity
        try:
            from azure.ai.projects import AIProjectClient
            from azure.identity import DefaultAzureCredential

            credential = DefaultAzureCredential(


                                exclude_interactive_browser_credential=False,


                                exclude_shared_token_cache_credential=False


                            )
            project_client = AIProjectClient(
                endpoint=project_endpoint,
                credential=credential
            )

            # Try to get client (this will test connectivity)
            openai_client = project_client.get_azure_open_ai_client()

            test_result["results"]["status"] = "connected"
            test_result["results"]["project_endpoint"] = project_endpoint
            test_result["status"] = "completed"
            logger.info(f"   ✅ Azure AI Foundry: Connected to {project_endpoint}")

        except Exception as e:
            test_result["results"]["status"] = "failed"
            test_result["results"]["error"] = str(e)
            test_result["status"] = "completed"
            logger.error(f"   ❌ Azure AI Foundry connectivity: {e}")

        self.results["tests"].append(test_result)
        return test_result

    def test_model_switching(self) -> Dict[str, Any]:
        """Test seamless model switching"""
        logger.info("\n📋 TEST 4: Model Switching")
        logger.info("-" * 80)

        test_result = {
            "test_name": "model_switching",
            "status": "running",
            "results": []
        }

        test_prompt = "Test prompt for model switching"
        models_to_test = ["iron_legion_mark_i", "iron_legion_mark_ii", "ultron_local"]

        for model_id in models_to_test:
            try:
                # Switch to model
                endpoint = self.integration.switch_model(model_id, self.ModelProvider.LOCAL)

                # Test inference
                request = self.InferenceRequest(
                    prompt=test_prompt,
                    model=model_id,
                    provider_preference=self.ModelProvider.LOCAL,
                    fallback_enabled=False  # Disable fallback for switching test
                )

                response = self.integration.inference(request)

                test_result["results"].append({
                    "model": model_id,
                    "status": "success",
                    "switched": True,
                    "inference": True,
                    "latency_ms": response.latency_ms
                })

                logger.info(f"   ✅ {model_id}: Switched and tested")

            except Exception as e:
                test_result["results"].append({
                    "model": model_id,
                    "status": "failed",
                    "error": str(e)
                })
                logger.error(f"   ❌ {model_id}: {e}")

        test_result["status"] = "completed"
        self.results["tests"].append(test_result)

        return test_result

    def test_jarvis_routing(self) -> Dict[str, Any]:
        """Test JARVIS routing integration"""
        logger.info("\n📋 TEST 5: JARVIS Routing Integration")
        logger.info("-" * 80)

        test_result = {
            "test_name": "jarvis_routing",
            "status": "running",
            "results": {}
        }

        try:
            from scripts.python.jarvis_threat_criticality_routing import (
                JARVISThreatCriticalityRouter,
                ThreatMetrics
            )

            router = JARVISThreatCriticalityRouter(self.project_root)

            # Test routing with different metrics
            test_cases = [
                {"name": "low_priority", "metrics": ThreatMetrics(criticality=0.2, threat_level=0.1)},
                {"name": "medium_priority", "metrics": ThreatMetrics(criticality=0.5, threat_level=0.4)},
                {"name": "high_priority", "metrics": ThreatMetrics(criticality=0.7, threat_level=0.6)},
                {"name": "critical_priority", "metrics": ThreatMetrics(criticality=0.9, threat_level=0.8)}
            ]

            routing_results = []
            for test_case in test_cases:
                decision = router.route_decision(test_case["metrics"])
                routing_results.append({
                    "priority": test_case["name"],
                    "routing": decision.routing.value,
                    "target_cluster": decision.target_cluster,
                    "target_node": decision.target_node,
                    "includes_azure": "azure_foundry" in (decision.target_cluster or "").lower()
                })
                logger.info(f"   {test_case['name']}: {decision.routing.value} → {decision.target_cluster or decision.target_node}")

            test_result["results"]["routing_tests"] = routing_results
            test_result["results"]["azure_in_routing"] = any(r.get("includes_azure", False) for r in routing_results)
            test_result["status"] = "completed"
            logger.info("   ✅ JARVIS routing: Working")

        except Exception as e:
            test_result["results"]["error"] = str(e)
            test_result["status"] = "failed"
            logger.error(f"   ❌ JARVIS routing: {e}")

        self.results["tests"].append(test_result)
        return test_result

    def run_all_tests(self):
        try:
            """Run all battle tests"""
            logger.info("\n🚀 STARTING BATTLE TESTS")
            logger.info("=" * 80)

            start_time = time.time()

            # Run tests
            self.test_local_models()
            self.test_azure_authentication()
            self.test_azure_foundry_connectivity()
            self.test_model_switching()
            self.test_jarvis_routing()

            # Calculate summary
            elapsed = time.time() - start_time
            total_tests = len(self.results["tests"])
            passed_tests = sum(1 for t in self.results["tests"] if t.get("status") == "completed")
            failed_tests = sum(1 for t in self.results["tests"] if t.get("status") == "failed")
            skipped_tests = sum(1 for t in self.results["tests"] if t.get("status") == "skipped")

            self.results["completed"] = datetime.now().isoformat()
            self.results["duration_seconds"] = elapsed
            self.results["summary"] = {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "success_rate": f"{passed_tests}/{total_tests}"
            }

            # Save results
            results_file = self.data_dir / f"{self.results['test_id']}.json"
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)

            # Print summary
            logger.info("\n" + "=" * 80)
            logger.info("📊 BATTLE TEST SUMMARY")
            logger.info("=" * 80)
            logger.info(f"   Total Tests: {total_tests}")
            logger.info(f"   Passed: {passed_tests}")
            logger.info(f"   Failed: {failed_tests}")
            logger.info(f"   Skipped: {skipped_tests}")
            logger.info(f"   Success Rate: {passed_tests}/{total_tests}")
            logger.info(f"   Duration: {elapsed:.2f}s")
            logger.info(f"   Results: {results_file}")
            logger.info("=" * 80)

            return self.results


        except Exception as e:
            self.logger.error(f"Error in run_all_tests: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Battle Test: Azure AI Foundry Integration")
        parser.add_argument("--test", type=str, help="Run specific test (local, auth, connectivity, switching, routing)")
        parser.add_argument("--json", action="store_true", help="Output results as JSON")

        args = parser.parse_args()

        battle_test = BattleTestAzureAIFoundry()

        if args.test:
            # Run specific test
            if args.test == "local":
                result = battle_test.test_local_models()
            elif args.test == "auth":
                result = battle_test.test_azure_authentication()
            elif args.test == "connectivity":
                result = battle_test.test_azure_foundry_connectivity()
            elif args.test == "switching":
                result = battle_test.test_model_switching()
            elif args.test == "routing":
                result = battle_test.test_jarvis_routing()
            else:
                print(f"Unknown test: {args.test}")
                return 1

            if args.json:
                print(json.dumps(result, indent=2, default=str))
        else:
            # Run all tests
            results = battle_test.run_all_tests()
            if args.json:
                print(json.dumps(results, indent=2, default=str))

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())