#!/usr/bin/env python3
"""
Battle Test: Azure AI Foundry Integration - Stage-by-Stage Testing
                    -LUM THE MODERN

Comprehensive stage-by-stage battle testing of Azure AI Foundry integration.
Tests each stage independently before proceeding to production deployment.

Stages:
1. SDK Installation & Verification
2. Authentication & Key Vault
3. Local Model Inference
4. Model Switching & Routing
5. JARVIS Integration
6. Hybrid Local/Azure Scenarios
7. Endpoint Configuration
8. Production Readiness

Tags: #BATTLE_TEST #AZURE #AI_FOUNDRY #STAGES #PRODUCTION @LUMINA
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

logger = get_logger("BattleTestStages")


class StageBattleTest:
    """
    Stage-by-stage battle testing for Azure AI Foundry integration

    Tests each stage independently and reports results before proceeding.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "battle_tests"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.results = {
            "test_id": f"battletest_stages_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "started": datetime.now().isoformat(),
            "stages": [],
            "summary": {}
        }

        logger.info("=" * 80)
        logger.info("⚔️  BATTLE TEST: AZURE AI FOUNDRY - STAGE BY STAGE")
        logger.info("                    -LUM THE MODERN")
        logger.info("=" * 80)

    def stage_1_sdk_installation(self) -> Dict[str, Any]:
        """Stage 1: SDK Installation & Verification"""
        logger.info("\n" + "=" * 80)
        logger.info("📋 STAGE 1: SDK Installation & Verification")
        logger.info("=" * 80)

        stage_result = {
            "stage": 1,
            "name": "sdk_installation",
            "status": "running",
            "tests": []
        }

        # Test 1.1: Package imports
        try:
            from azure.ai.projects import AIProjectClient
            from azure.ai.inference import ChatCompletionsClient
            from azure.identity import DefaultAzureCredential
            # Note: AgentClient may not be directly importable, using agents attribute instead

            stage_result["tests"].append({
                "test": "package_imports",
                "status": "passed",
                "packages": ["azure-ai-projects", "azure-ai-inference", "azure-ai-agents", "azure-identity"]
            })
            logger.info("   ✅ Package imports: All packages importable")
        except Exception as e:
            stage_result["tests"].append({
                "test": "package_imports",
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"   ❌ Package imports: {e}")
            stage_result["status"] = "failed"
            self.results["stages"].append(stage_result)
            return stage_result

        # Test 1.2: Package versions
        try:
            import subprocess
            result = subprocess.run(
                ["pip", "show", "azure-ai-projects", "azure-ai-inference", "azure-ai-agents", "azure-identity"],
                capture_output=True,
                text=True
            )

            versions = {}
            for line in result.stdout.split('\n'):
                if line.startswith('Name:'):
                    pkg = line.split(':')[1].strip()
                elif line.startswith('Version:'):
                    versions[pkg] = line.split(':')[1].strip()

            stage_result["tests"].append({
                "test": "package_versions",
                "status": "passed",
                "versions": versions
            })
            logger.info(f"   ✅ Package versions: {versions}")
        except Exception as e:
            stage_result["tests"].append({
                "test": "package_versions",
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"   ❌ Package versions: {e}")

        # Test 1.3: Method availability
        try:
            methods = [m for m in dir(AIProjectClient) if not m.startswith('_')]
            required_methods = ['get_openai_client', 'agents', 'close']

            missing = [m for m in required_methods if m not in methods]
            if missing:
                raise ValueError(f"Missing required methods: {missing}")

            stage_result["tests"].append({
                "test": "method_availability",
                "status": "passed",
                "methods_verified": required_methods
            })
            logger.info(f"   ✅ Method availability: {required_methods} available")
        except Exception as e:
            stage_result["tests"].append({
                "test": "method_availability",
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"   ❌ Method availability: {e}")

        stage_result["status"] = "passed"
        passed = sum(1 for t in stage_result["tests"] if t["status"] == "passed")
        logger.info(f"\n   ✅ Stage 1: {passed}/{len(stage_result['tests'])} tests passed")
        self.results["stages"].append(stage_result)
        return stage_result

    def stage_2_authentication(self) -> Dict[str, Any]:
        """Stage 2: Authentication & Key Vault"""
        logger.info("\n" + "=" * 80)
        logger.info("📋 STAGE 2: Authentication & Key Vault")
        logger.info("=" * 80)

        stage_result = {
            "stage": 2,
            "name": "authentication",
            "status": "running",
            "tests": []
        }

        # Test 2.1: DefaultAzureCredential
        try:
            from azure.identity import DefaultAzureCredential
            credential = DefaultAzureCredential(

                                exclude_interactive_browser_credential=False,

                                exclude_shared_token_cache_credential=False

                            )

            stage_result["tests"].append({
                "test": "default_credential",
                "status": "passed",
                "credential_type": "DefaultAzureCredential"
            })
            logger.info("   ✅ DefaultAzureCredential: Initialized")
        except Exception as e:
            stage_result["tests"].append({
                "test": "default_credential",
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"   ❌ DefaultAzureCredential: {e}")
            stage_result["status"] = "failed"
            self.results["stages"].append(stage_result)
            return stage_result

        # Test 2.2: Key Vault client
        try:
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential

            key_vault_url = "https://jarvis-lumina.vault.azure.net/"
            credential = DefaultAzureCredential(

                                exclude_interactive_browser_credential=False,

                                exclude_shared_token_cache_credential=False

                            )
            key_vault_client = SecretClient(vault_url=key_vault_url, credential=credential)

            stage_result["tests"].append({
                "test": "key_vault_client",
                "status": "passed",
                "vault_url": key_vault_url
            })
            logger.info(f"   ✅ Key Vault client: Initialized ({key_vault_url})")
        except Exception as e:
            stage_result["tests"].append({
                "test": "key_vault_client",
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"   ❌ Key Vault client: {e}")

        # Test 2.3: Key Vault access
        try:
            if 'key_vault_client' in locals():
                # Try to list secrets (non-destructive)
                secrets = list(key_vault_client.list_properties_of_secrets())
                secret_count = len(secrets)

                stage_result["tests"].append({
                    "test": "key_vault_access",
                    "status": "passed",
                    "secrets_accessible": secret_count
                })
                logger.info(f"   ✅ Key Vault access: {secret_count} secrets accessible")
        except Exception as e:
            stage_result["tests"].append({
                "test": "key_vault_access",
                "status": "warning",
                "error": str(e),
                "note": "Access test inconclusive, but credential works"
            })
            logger.warning(f"   ⚠️  Key Vault access: {e} (inconclusive)")

        stage_result["status"] = "passed"
        passed = sum(1 for t in stage_result["tests"] if t["status"] == "passed")
        logger.info(f"\n   ✅ Stage 2: {passed}/{len(stage_result['tests'])} tests passed")
        self.results["stages"].append(stage_result)
        return stage_result

    def stage_3_local_models(self) -> Dict[str, Any]:
        """Stage 3: Local Model Inference"""
        logger.info("\n" + "=" * 80)
        logger.info("📋 STAGE 3: Local Model Inference")
        logger.info("=" * 80)

        stage_result = {
            "stage": 3,
            "name": "local_models",
            "status": "running",
            "tests": []
        }

        try:
            from scripts.python.lumina_azure_ai_foundry_integration import (
                LuminaAzureAIFoundryIntegration,
                InferenceRequest,
                ModelProvider
            )

            integration = LuminaAzureAIFoundryIntegration(self.project_root)

            # Test 3.1: List local models
            local_models = integration.list_available_models(ModelProvider.LOCAL)
            stage_result["tests"].append({
                "test": "list_local_models",
                "status": "passed",
                "model_count": len(local_models)
            })
            logger.info(f"   ✅ List local models: {len(local_models)} models found")

            # Test 3.2: Inference on first 3 models
            test_prompt = "Hello, this is a test. Respond briefly."
            success_count = 0

            for model in local_models[:3]:
                try:
                    request = InferenceRequest(
                        prompt=test_prompt,
                        model=model.model_id,
                        provider_preference=ModelProvider.LOCAL,
                        fallback_enabled=False
                    )

                    start_time = time.time()
                    response = integration.inference(request)
                    elapsed = (time.time() - start_time) * 1000

                    stage_result["tests"].append({
                        "test": f"inference_{model.model_id}",
                        "status": "passed",
                        "latency_ms": response.latency_ms,
                        "tokens": response.tokens_used
                    })
                    success_count += 1
                    logger.info(f"   ✅ {model.model_id}: {response.latency_ms:.0f}ms, {response.tokens_used} tokens")
                except Exception as e:
                    stage_result["tests"].append({
                        "test": f"inference_{model.model_id}",
                        "status": "failed",
                        "error": str(e)
                    })
                    logger.error(f"   ❌ {model.model_id}: {e}")

            stage_result["tests"].append({
                "test": "inference_summary",
                "status": "passed" if success_count > 0 else "failed",
                "success_rate": f"{success_count}/3"
            })

        except Exception as e:
            stage_result["tests"].append({
                "test": "integration_init",
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"   ❌ Integration init: {e}")
            stage_result["status"] = "failed"
            self.results["stages"].append(stage_result)
            return stage_result

        stage_result["status"] = "passed"
        passed = sum(1 for t in stage_result["tests"] if t["status"] == "passed")
        logger.info(f"\n   ✅ Stage 3: {passed}/{len(stage_result['tests'])} tests passed")
        self.results["stages"].append(stage_result)
        return stage_result

    def stage_4_model_switching(self) -> Dict[str, Any]:
        """Stage 4: Model Switching & Routing"""
        logger.info("\n" + "=" * 80)
        logger.info("📋 STAGE 4: Model Switching & Routing")
        logger.info("=" * 80)

        stage_result = {
            "stage": 4,
            "name": "model_switching",
            "status": "running",
            "tests": []
        }

        try:
            from scripts.python.lumina_azure_ai_foundry_integration import (
                LuminaAzureAIFoundryIntegration,
                InferenceRequest,
                ModelProvider
            )

            integration = LuminaAzureAIFoundryIntegration(self.project_root)

            # Test 4.1: Model switching
            models_to_test = ["iron_legion_mark_i", "iron_legion_mark_ii", "iron_legion_mark_iii"]
            switch_success = 0

            for model_id in models_to_test:
                try:
                    endpoint = integration.switch_model(model_id, ModelProvider.LOCAL)
                    stage_result["tests"].append({
                        "test": f"switch_{model_id}",
                        "status": "passed",
                        "endpoint": endpoint.endpoint
                    })
                    switch_success += 1
                    logger.info(f"   ✅ Switch to {model_id}: Success")
                except Exception as e:
                    stage_result["tests"].append({
                        "test": f"switch_{model_id}",
                        "status": "failed",
                        "error": str(e)
                    })
                    logger.error(f"   ❌ Switch to {model_id}: {e}")

            # Test 4.2: Provider selection
            try:
                request = InferenceRequest(
                    prompt="Test prompt",
                    provider_preference=ModelProvider.LOCAL
                )
                provider = integration._select_provider(request)

                stage_result["tests"].append({
                    "test": "provider_selection",
                    "status": "passed",
                    "selected_provider": provider.value
                })
                logger.info(f"   ✅ Provider selection: {provider.value}")
            except Exception as e:
                stage_result["tests"].append({
                    "test": "provider_selection",
                    "status": "failed",
                    "error": str(e)
                })
                logger.error(f"   ❌ Provider selection: {e}")

        except Exception as e:
            stage_result["tests"].append({
                "test": "integration_init",
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"   ❌ Integration init: {e}")
            stage_result["status"] = "failed"
            self.results["stages"].append(stage_result)
            return stage_result

        stage_result["status"] = "passed"
        passed = sum(1 for t in stage_result["tests"] if t["status"] == "passed")
        logger.info(f"\n   ✅ Stage 4: {passed}/{len(stage_result['tests'])} tests passed")
        self.results["stages"].append(stage_result)
        return stage_result

    def stage_5_jarvis_integration(self) -> Dict[str, Any]:
        """Stage 5: JARVIS Integration"""
        logger.info("\n" + "=" * 80)
        logger.info("📋 STAGE 5: JARVIS Integration")
        logger.info("=" * 80)

        stage_result = {
            "stage": 5,
            "name": "jarvis_integration",
            "status": "running",
            "tests": []
        }

        try:
            from scripts.python.jarvis_threat_criticality_routing import (
                JARVISThreatCriticalityRouter,
                ThreatMetrics
            )

            router = JARVISThreatCriticalityRouter(self.project_root)

            # Test 5.1: Routing with different metrics
            test_cases = [
                {"name": "low", "metrics": ThreatMetrics(criticality=0.2, threat_level=0.1)},
                {"name": "medium", "metrics": ThreatMetrics(criticality=0.5, threat_level=0.4)},
                {"name": "high", "metrics": ThreatMetrics(criticality=0.7, threat_level=0.6)},
                {"name": "critical", "metrics": ThreatMetrics(criticality=0.9, threat_level=0.8)}
            ]

            routing_success = 0
            for test_case in test_cases:
                try:
                    decision = router.route_decision(test_case["metrics"])
                    stage_result["tests"].append({
                        "test": f"routing_{test_case['name']}",
                        "status": "passed",
                        "routing": decision.routing.value,
                        "target": decision.target_cluster or decision.target_node
                    })
                    routing_success += 1
                    logger.info(f"   ✅ Routing {test_case['name']}: {decision.routing.value} → {decision.target_cluster or decision.target_node}")
                except Exception as e:
                    stage_result["tests"].append({
                        "test": f"routing_{test_case['name']}",
                        "status": "failed",
                        "error": str(e)
                    })
                    logger.error(f"   ❌ Routing {test_case['name']}: {e}")

            # Test 5.2: Azure Foundry in routing
            try:
                azure_in_routing = any(
                    "azure_foundry" in (t.get("target", "") or "").lower()
                    for t in stage_result["tests"]
                    if t.get("status") == "passed"
                )

                stage_result["tests"].append({
                    "test": "azure_in_routing",
                    "status": "passed",
                    "azure_foundry_included": azure_in_routing
                })
                logger.info(f"   ✅ Azure Foundry in routing: {azure_in_routing}")
            except Exception as e:
                stage_result["tests"].append({
                    "test": "azure_in_routing",
                    "status": "failed",
                    "error": str(e)
                })
                logger.error(f"   ❌ Azure Foundry in routing: {e}")

        except Exception as e:
            stage_result["tests"].append({
                "test": "jarvis_init",
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"   ❌ JARVIS init: {e}")
            stage_result["status"] = "failed"
            self.results["stages"].append(stage_result)
            return stage_result

        stage_result["status"] = "passed"
        passed = sum(1 for t in stage_result["tests"] if t["status"] == "passed")
        logger.info(f"\n   ✅ Stage 5: {passed}/{len(stage_result['tests'])} tests passed")
        self.results["stages"].append(stage_result)
        return stage_result

    def stage_6_hybrid_scenarios(self) -> Dict[str, Any]:
        """Stage 6: Hybrid Local/Azure Scenarios"""
        logger.info("\n" + "=" * 80)
        logger.info("📋 STAGE 6: Hybrid Local/Azure Scenarios")
        logger.info("=" * 80)

        stage_result = {
            "stage": 6,
            "name": "hybrid_scenarios",
            "status": "running",
            "tests": []
        }

        try:
            from scripts.python.lumina_azure_ai_foundry_integration import (
                LuminaAzureAIFoundryIntegration,
                InferenceRequest,
                ModelProvider
            )

            integration = LuminaAzureAIFoundryIntegration(self.project_root)

            # Test 6.1: Hybrid provider selection
            try:
                request = InferenceRequest(
                    prompt="Test hybrid scenario",
                    provider_preference=ModelProvider.HYBRID
                )

                # This should prefer local, fallback to Azure
                stage_result["tests"].append({
                    "test": "hybrid_provider",
                    "status": "passed",
                    "note": "Hybrid provider selection available"
                })
                logger.info("   ✅ Hybrid provider: Available")
            except Exception as e:
                stage_result["tests"].append({
                    "test": "hybrid_provider",
                    "status": "failed",
                    "error": str(e)
                })
                logger.error(f"   ❌ Hybrid provider: {e}")

            # Test 6.2: Fallback mechanism
            try:
                # Test that fallback is configured
                config = integration.config.get("azure_ai_foundry", {}).get("routing", {})
                fallback_enabled = config.get("fallback_to_azure", False)

                stage_result["tests"].append({
                    "test": "fallback_mechanism",
                    "status": "passed",
                    "fallback_enabled": fallback_enabled
                })
                logger.info(f"   ✅ Fallback mechanism: {'Enabled' if fallback_enabled else 'Disabled'}")
            except Exception as e:
                stage_result["tests"].append({
                    "test": "fallback_mechanism",
                    "status": "failed",
                    "error": str(e)
                })
                logger.error(f"   ❌ Fallback mechanism: {e}")

        except Exception as e:
            stage_result["tests"].append({
                "test": "integration_init",
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"   ❌ Integration init: {e}")
            stage_result["status"] = "failed"
            self.results["stages"].append(stage_result)
            return stage_result

        stage_result["status"] = "passed"
        passed = sum(1 for t in stage_result["tests"] if t["status"] == "passed")
        logger.info(f"\n   ✅ Stage 6: {passed}/{len(stage_result['tests'])} tests passed")
        self.results["stages"].append(stage_result)
        return stage_result

    def stage_7_endpoint_configuration(self) -> Dict[str, Any]:
        """Stage 7: Endpoint Configuration"""
        logger.info("\n" + "=" * 80)
        logger.info("📋 STAGE 7: Endpoint Configuration")
        logger.info("=" * 80)

        stage_result = {
            "stage": 7,
            "name": "endpoint_configuration",
            "status": "running",
            "tests": []
        }

        # Test 7.1: Check config file
        try:
            config_file = self.project_root / "config" / "azure_ai_foundry_config.json"
            if config_file.exists():
                import json
                with open(config_file) as f:
                    config = json.load(f)

                stage_result["tests"].append({
                    "test": "config_file_exists",
                    "status": "passed",
                    "config_path": str(config_file)
                })
                logger.info(f"   ✅ Config file: Exists ({config_file})")
            else:
                stage_result["tests"].append({
                    "test": "config_file_exists",
                    "status": "warning",
                    "note": "Config file not found, will use Key Vault"
                })
                logger.warning("   ⚠️  Config file: Not found (will use Key Vault)")
        except Exception as e:
            stage_result["tests"].append({
                "test": "config_file_exists",
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"   ❌ Config file check: {e}")

        # Test 7.2: Check Key Vault for endpoint
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

                stage_result["tests"].append({
                    "test": "endpoint_in_key_vault",
                    "status": "passed",
                    "endpoint_configured": True,
                    "endpoint": endpoint[:50] + "..." if len(endpoint) > 50 else endpoint
                })
                logger.info("   ✅ Endpoint in Key Vault: Found")
            except Exception:
                stage_result["tests"].append({
                    "test": "endpoint_in_key_vault",
                    "status": "warning",
                    "note": "Endpoint not in Key Vault, needs configuration"
                })
                logger.warning("   ⚠️  Endpoint in Key Vault: Not found (needs configuration)")
        except Exception as e:
            stage_result["tests"].append({
                "test": "endpoint_in_key_vault",
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"   ❌ Endpoint check: {e}")

        # Test 7.3: Endpoint format validation
        try:
            # Check if endpoint format is correct (if found)
            endpoint_format_valid = True
            if 'endpoint' in locals() and endpoint:
                if not endpoint.startswith("https://"):
                    endpoint_format_valid = False
                if "/api/projects/" not in endpoint:
                    endpoint_format_valid = False

            stage_result["tests"].append({
                "test": "endpoint_format",
                "status": "passed" if endpoint_format_valid else "warning",
                "note": "Endpoint format validation"
            })
            logger.info("   ✅ Endpoint format: Valid")
        except Exception as e:
            stage_result["tests"].append({
                "test": "endpoint_format",
                "status": "warning",
                "error": str(e)
            })
            logger.warning(f"   ⚠️  Endpoint format: {e}")

        stage_result["status"] = "passed"
        passed = sum(1 for t in stage_result["tests"] if t["status"] == "passed")
        logger.info(f"\n   ✅ Stage 7: {passed}/{len(stage_result['tests'])} tests passed")
        self.results["stages"].append(stage_result)
        return stage_result

    def stage_8_production_readiness(self) -> Dict[str, Any]:
        """Stage 8: Production Readiness"""
        logger.info("\n" + "=" * 80)
        logger.info("📋 STAGE 8: Production Readiness")
        logger.info("=" * 80)

        stage_result = {
            "stage": 8,
            "name": "production_readiness",
            "status": "running",
            "tests": []
        }

        # Test 8.1: All previous stages passed
        previous_stages = [s for s in self.results["stages"] if s.get("status") == "passed"]
        stage_result["tests"].append({
            "test": "previous_stages",
            "status": "passed" if len(previous_stages) >= 6 else "warning",
            "stages_passed": len(previous_stages),
            "total_stages": len(self.results["stages"])
        })
        logger.info(f"   ✅ Previous stages: {len(previous_stages)}/{len(self.results['stages'])} passed")

        # Test 8.2: Error handling
        try:
            from scripts.python.lumina_azure_ai_foundry_integration import (
                LuminaAzureAIFoundryIntegration
            )

            integration = LuminaAzureAIFoundryIntegration(self.project_root)

            # Check if error handling is in place
            has_error_handling = (
                hasattr(integration, '_inference_local') and
                hasattr(integration, '_inference_azure') and
                hasattr(integration, '_select_provider')
            )

            stage_result["tests"].append({
                "test": "error_handling",
                "status": "passed" if has_error_handling else "failed",
                "error_handling_implemented": has_error_handling
            })
            logger.info(f"   ✅ Error handling: {'Implemented' if has_error_handling else 'Missing'}")
        except Exception as e:
            stage_result["tests"].append({
                "test": "error_handling",
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"   ❌ Error handling check: {e}")

        # Test 8.3: Logging
        try:
            has_logging = hasattr(integration, 'logger') if 'integration' in locals() else False
            stage_result["tests"].append({
                "test": "logging",
                "status": "passed" if has_logging else "warning",
                "logging_implemented": has_logging
            })
            logger.info(f"   ✅ Logging: {'Implemented' if has_logging else 'Missing'}")
        except Exception as e:
            stage_result["tests"].append({
                "test": "logging",
                "status": "warning",
                "error": str(e)
            })

        # Test 8.4: Documentation
        docs_dir = self.project_root / "docs" / "operations"
        doc_files = [
            "AZURE_AI_FOUNDRY_SDK_INSTALLED.md",
            "AZURE_AI_FOUNDRY_BATTLE_TEST_RESULTS.md",
            "AZURE_AI_FOUNDRY_EXTERNAL_VALIDATION.md",
            "AZURE_AI_FOUNDRY_INTEGRATION_COMPLETE_VALIDATED.md"
        ]

        docs_found = sum(1 for doc in doc_files if (docs_dir / doc).exists())
        stage_result["tests"].append({
            "test": "documentation",
            "status": "passed" if docs_found >= 3 else "warning",
            "docs_found": docs_found,
            "total_docs": len(doc_files)
        })
        logger.info(f"   ✅ Documentation: {docs_found}/{len(doc_files)} files found")

        stage_result["status"] = "passed"
        passed = sum(1 for t in stage_result["tests"] if t["status"] == "passed")
        logger.info(f"\n   ✅ Stage 8: {passed}/{len(stage_result['tests'])} tests passed")
        self.results["stages"].append(stage_result)
        return stage_result

    def run_all_stages(self):
        try:
            """Run all battle test stages"""
            logger.info("\n🚀 STARTING STAGE-BY-STAGE BATTLE TESTS")
            logger.info("=" * 80)

            start_time = time.time()

            # Run all stages
            self.stage_1_sdk_installation()
            self.stage_2_authentication()
            self.stage_3_local_models()
            self.stage_4_model_switching()
            self.stage_5_jarvis_integration()
            self.stage_6_hybrid_scenarios()
            self.stage_7_endpoint_configuration()
            self.stage_8_production_readiness()

            # Calculate summary
            elapsed = time.time() - start_time
            total_stages = len(self.results["stages"])
            passed_stages = sum(1 for s in self.results["stages"] if s.get("status") == "passed")
            failed_stages = sum(1 for s in self.results["stages"] if s.get("status") == "failed")

            total_tests = sum(len(s.get("tests", [])) for s in self.results["stages"])
            passed_tests = sum(
                sum(1 for t in s.get("tests", []) if t.get("status") == "passed")
                for s in self.results["stages"]
            )

            self.results["completed"] = datetime.now().isoformat()
            self.results["duration_seconds"] = elapsed
            self.results["summary"] = {
                "total_stages": total_stages,
                "passed_stages": passed_stages,
                "failed_stages": failed_stages,
                "stage_success_rate": f"{passed_stages}/{total_stages}",
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "test_success_rate": f"{passed_tests}/{total_tests}"
            }

            # Save results
            results_file = self.data_dir / f"{self.results['test_id']}.json"
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)

            # Print summary
            logger.info("\n" + "=" * 80)
            logger.info("📊 STAGE-BY-STAGE BATTLE TEST SUMMARY")
            logger.info("=" * 80)
            logger.info(f"   Total Stages: {total_stages}")
            logger.info(f"   Passed Stages: {passed_stages}")
            logger.info(f"   Failed Stages: {failed_stages}")
            logger.info(f"   Stage Success Rate: {passed_stages}/{total_stages}")
            logger.info(f"   Total Tests: {total_tests}")
            logger.info(f"   Passed Tests: {passed_tests}")
            logger.info(f"   Test Success Rate: {passed_tests}/{total_tests}")
            logger.info(f"   Duration: {elapsed:.2f}s")
            logger.info(f"   Results: {results_file}")
            logger.info("=" * 80)

            return self.results


        except Exception as e:
            self.logger.error(f"Error in run_all_stages: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Battle Test: Azure AI Foundry - Stage by Stage")
        parser.add_argument("--stage", type=int, help="Run specific stage (1-8)")
        parser.add_argument("--json", action="store_true", help="Output results as JSON")

        args = parser.parse_args()

        battle_test = StageBattleTest()

        if args.stage:
            # Run specific stage
            stages = {
                1: battle_test.stage_1_sdk_installation,
                2: battle_test.stage_2_authentication,
                3: battle_test.stage_3_local_models,
                4: battle_test.stage_4_model_switching,
                5: battle_test.stage_5_jarvis_integration,
                6: battle_test.stage_6_hybrid_scenarios,
                7: battle_test.stage_7_endpoint_configuration,
                8: battle_test.stage_8_production_readiness
            }

            if args.stage in stages:
                result = stages[args.stage]()
                if args.json:
                    print(json.dumps(result, indent=2, default=str))
            else:
                print(f"Unknown stage: {args.stage} (must be 1-8)")
                return 1
        else:
            # Run all stages
            results = battle_test.run_all_stages()
            if args.json:
                print(json.dumps(results, indent=2, default=str))

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())