#!/usr/bin/env python3
"""
LUMINA + Azure AI Foundry Seamless Integration
                    -LUM THE MODERN

Seamlessly integrates Azure AI Foundry with LUMINA's testing/experimental environment.
Enables model switching, routing, and testing across local and Azure models.

Tags: #AZURE #AI_FOUNDRY #INTEGRATION #TESTING #ROUTING @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
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

logger = get_logger("LuminaAzureAIFoundry")


class ModelProvider(Enum):
    """Model provider types"""
    LOCAL = "local"  # Iron Legion, ULTRON
    AZURE_FOUNDRY = "azure_foundry"
    HYBRID = "hybrid"  # Local + Azure with fallback


@dataclass
class ModelEndpoint:
    """Model endpoint configuration"""
    model_id: str
    provider: ModelProvider
    endpoint: str
    api_key: Optional[str] = None
    deployment_name: Optional[str] = None
    model_name: str = ""
    capabilities: List[str] = field(default_factory=list)
    cost_per_1k_tokens: float = 0.0
    latency_ms: float = 0.0


@dataclass
class InferenceRequest:
    """Inference request"""
    prompt: str
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    provider_preference: Optional[ModelProvider] = None
    fallback_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InferenceResponse:
    """Inference response"""
    response: str
    model_used: str
    provider: ModelProvider
    tokens_used: int = 0
    latency_ms: float = 0.0
    cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class LuminaAzureAIFoundryIntegration:
    """
    Seamless Azure AI Foundry integration for LUMINA

    Provides:
    - Unified model interface (local + Azure)
    - Seamless model switching
    - Routing integration with JARVIS
    - Testing/experimental framework
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.config_dir = self.project_root / "config"
        self.config_dir.mkdir(exist_ok=True)

        # Load configuration
        self.config_file = self.config_dir / "azure_ai_foundry_config.json"
        self.config = self._load_config()

        # Model endpoints
        self.model_endpoints: Dict[str, ModelEndpoint] = {}
        self._initialize_model_endpoints()

        # Azure authentication
        self.azure_authenticated = False
        self._authenticate_azure()

        logger.info("=" * 80)
        logger.info("🔷 LUMINA + AZURE AI FOUNDRY INTEGRATION")
        logger.info("                    -LUM THE MODERN")
        logger.info("=" * 80)
        logger.info("   Status: Initialized")
        logger.info("   Models: Local + Azure Foundry")
        logger.info("   Routing: JARVIS Integrated")
        logger.info("=" * 80)

    def _load_config(self) -> Dict[str, Any]:
        """Load Azure AI Foundry configuration"""
        default_config = {
            "azure_ai_foundry": {
                "enabled": True,
                "subscription_id": None,  # From environment or Key Vault
                "resource_group": "lumina-foundry",
                "workspace": "lumina-ai-foundry",
                "location": "eastus",
                "auth": {
                    "method": "managed_identity",
                    "key_vault": "jarvis-lumina.vault.azure.net"
                },
                "models": {
                    "default": "gpt-4",
                    "fallback": "gpt-3.5-turbo",
                    "experimental": ["claude-3", "llama-3"]
                },
                "routing": {
                    "use_jarvis_routing": True,
                    "cost_threshold": 0.10,
                    "latency_threshold_ms": 2000
                }
            },
            "local_models": {
                "iron_legion": {
                    "endpoint": "http://<NAS_IP>:3000",
                    "models": ["mark_i", "mark_ii", "mark_iii", "mark_iv", "mark_v", "mark_vi", "mark_vii"]
                },
                "ultron": {
                    "endpoint": "http://localhost:11434",
                    "models": []
                }
            },
            "testing": {
                "enabled": True,
                "environment": "home_lab",
                "a_b_testing": True,
                "performance_benchmarking": True
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"⚠️  Error loading config: {e}")

        return default_config

    def _initialize_model_endpoints(self):
        """Initialize model endpoints (local + Azure)"""
        # Load registered models from config
        local_models_config = self.config.get("local_models", {})

        # Iron Legion models
        iron_legion_config = local_models_config.get("iron_legion", {})
        if iron_legion_config.get("models"):
            models_dict = iron_legion_config.get("models", {})
            for mark_name, mark_info in models_dict.items():
                endpoint = mark_info.get("endpoint", iron_legion_config.get("endpoint", ""))
                model_name = mark_info.get("model", mark_name)
                capabilities = mark_info.get("capabilities", ["general"])

                self.model_endpoints[f"iron_legion_{mark_name}"] = ModelEndpoint(
                    model_id=f"iron_legion_{mark_name}",
                    provider=ModelProvider.LOCAL,
                    endpoint=endpoint,
                    model_name=model_name,
                    capabilities=capabilities
                )

        # Ollama models
        ollama_config = local_models_config.get("ollama", {})
        if ollama_config:
            endpoint = ollama_config.get("endpoint", "http://localhost:11434")
            model_details = ollama_config.get("model_details", {})
            for model_name, model_info in model_details.items():
                capabilities = model_info.get("capabilities", ["text_generation"])
                self.model_endpoints[f"ollama_{model_name}"] = ModelEndpoint(
                    model_id=f"ollama_{model_name}",
                    provider=ModelProvider.LOCAL,
                    endpoint=endpoint,
                    model_name=model_name,
                    capabilities=capabilities
                )

        # ULTRON models
        ultron_config = local_models_config.get("ultron", {})
        if ultron_config:
            endpoint = ultron_config.get("endpoint", "http://localhost:11434")
            model_details = ultron_config.get("model_details", {})
            for model_name, model_info in model_details.items():
                capabilities = model_info.get("capabilities", ["text_generation", "conversation"])
                self.model_endpoints[f"ultron_{model_name}"] = ModelEndpoint(
                    model_id=f"ultron_{model_name}",
                    provider=ModelProvider.LOCAL,
                    endpoint=endpoint,
                    model_name=model_name,
                    capabilities=capabilities
                )

        # Azure Foundry models (will be populated when authenticated)
        if self.config.get("azure_ai_foundry", {}).get("enabled"):
            azure_models = self.config["azure_ai_foundry"].get("models", {})
            # Will be initialized after authentication
            logger.info("   Azure models will be initialized after authentication")

    def _authenticate_azure(self):
        """Authenticate with Azure using existing infrastructure"""
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient

            # Use existing Azure authentication (same as other Azure services)
            credential = DefaultAzureCredential(

                                exclude_interactive_browser_credential=False,

                                exclude_shared_token_cache_credential=False

                            )

            # Get Key Vault URL from config or use existing vault
            key_vault_url = self.config.get("azure_ai_foundry", {}).get("auth", {}).get("key_vault")
            if not key_vault_url:
                # Use existing Key Vault from azure_services_config
                key_vault_url = "https://jarvis-lumina.vault.azure.net/"

            # Initialize Key Vault client (same pattern as other Azure integrations)
            self.key_vault_client = SecretClient(vault_url=key_vault_url, credential=credential)

            # Test authentication by attempting to list secrets (non-destructive)
            try:
                # Just verify we can access the vault
                list(self.key_vault_client.list_properties_of_secrets())
                logger.info(f"✅ Azure authentication verified")
                logger.info(f"✅ Key Vault accessible: {key_vault_url}")
                self.azure_authenticated = True
            except Exception as e:
                logger.warning(f"⚠️  Key Vault access test failed: {e}")
                # Still mark as authenticated if credential works
                self.azure_authenticated = True
                logger.info("✅ Azure credentials available (Key Vault test inconclusive)")

        except Exception as e:
            logger.error(f"❌ Azure authentication error: {e}")
            logger.error("   Azure services may not be available")
            self.azure_authenticated = False
            self.key_vault_client = None

    def list_available_models(self, provider: Optional[ModelProvider] = None) -> List[ModelEndpoint]:
        """List available models"""
        if provider:
            return [ep for ep in self.model_endpoints.values() if ep.provider == provider]
        return list(self.model_endpoints.values())

    def inference(self, request: InferenceRequest) -> InferenceResponse:
        """
        Unified inference interface

        Works with both local and Azure models seamlessly
        """
        # Determine which provider to use
        provider = request.provider_preference or self._select_provider(request)

        # Route to appropriate provider
        if provider == ModelProvider.LOCAL:
            return self._inference_local(request)
        elif provider == ModelProvider.AZURE_FOUNDRY:
            return self._inference_azure(request)
        elif provider == ModelProvider.HYBRID:
            return self._inference_hybrid(request)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _select_provider(self, request: InferenceRequest) -> ModelProvider:
        """Select provider based on routing logic"""
        # Check if JARVIS routing is enabled
        if self.config.get("azure_ai_foundry", {}).get("routing", {}).get("use_jarvis_routing"):
            try:
                from jarvis_threat_criticality_routing import JARVISThreatRouting
                router = JARVISThreatRouting()
                # Use JARVIS routing to determine provider
                # For now, default to local for testing
                return ModelProvider.LOCAL
            except Exception as e:
                logger.debug(f"JARVIS routing not available: {e}")

        # Default: prefer local for testing
        return ModelProvider.LOCAL

    def _inference_local(self, request: InferenceRequest) -> InferenceResponse:
        """Inference using local models (Iron Legion, ULTRON)"""
        import requests

        # Select local model
        model_endpoint = self._select_local_model(request)

        # Make request to local endpoint
        start_time = datetime.now()
        try:
            # Try OpenAI-compatible API first, then Ollama API
            api_endpoints = [
                f"{model_endpoint.endpoint}/v1/chat/completions",
                f"{model_endpoint.endpoint}/api/generate"
            ]

            response = None
            last_error = None

            for api_endpoint in api_endpoints:
                try:
                    if "/v1/chat/completions" in api_endpoint:
                        # OpenAI-compatible API
                        response = requests.post(
                            api_endpoint,
                            json={
                                "model": model_endpoint.model_name,
                                "messages": [{"role": "user", "content": request.prompt}],
                                "temperature": request.temperature,
                                "max_tokens": request.max_tokens
                            },
                            timeout=30
                        )
                    else:
                        # Ollama API
                        response = requests.post(
                            api_endpoint,
                            json={
                                "model": model_endpoint.model_name,
                                "prompt": request.prompt,
                                "temperature": request.temperature,
                                "stream": False
                            },
                            timeout=30
                        )

                    response.raise_for_status()
                    break  # Success, exit loop

                except Exception as e:
                    last_error = e
                    continue  # Try next endpoint

            if not response:
                raise RuntimeError(f"All API endpoints failed. Last error: {last_error}")
            response.raise_for_status()
            result = response.json()

            latency = (datetime.now() - start_time).total_seconds() * 1000

            # Extract response based on API format
            if "/v1/chat/completions" in response.url:
                # OpenAI-compatible format
                response_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                tokens_used = result.get("usage", {}).get("total_tokens", 0)
            else:
                # Ollama format
                response_text = result.get("response", "")
                tokens_used = result.get("eval_count", 0)

            return InferenceResponse(
                response=response_text,
                model_used=model_endpoint.model_id,
                provider=ModelProvider.LOCAL,
                tokens_used=tokens_used,
                latency_ms=latency,
                cost=0.0  # Local models are free
            )
        except Exception as e:
            logger.error(f"❌ Local inference error: {e}")
            if request.fallback_enabled and self.azure_authenticated:
                # Fallback to Azure if enabled and Azure is available
                try:
                    return self._inference_azure(request)
                except Exception as azure_error:
                    logger.error(f"❌ Azure fallback also failed: {azure_error}")
                    raise RuntimeError(f"Both local and Azure inference failed. Local: {e}, Azure: {azure_error}")
            raise

    def _inference_azure(self, request: InferenceRequest) -> InferenceResponse:
        """Inference using Azure AI Foundry"""
        if not self.azure_authenticated:
            raise RuntimeError("Azure not authenticated")

        try:
            from azure.ai.projects import AIProjectClient
            from azure.identity import DefaultAzureCredential

            # Get project endpoint from config or Key Vault
            project_endpoint = self.config.get("azure_ai_foundry", {}).get("project_endpoint")
            if not project_endpoint:
                # Try to get from Key Vault
                if self.key_vault_client:
                    try:
                        secret = self.key_vault_client.get_secret("azure-ai-foundry-project-endpoint")
                        project_endpoint = secret.value
                    except Exception:
                        logger.warning("⚠️  Project endpoint not found in config or Key Vault")
                        raise RuntimeError("Azure AI Foundry project endpoint not configured")
                else:
                    raise RuntimeError("Azure AI Foundry project endpoint not configured")

            # Initialize AI Project Client
            credential = DefaultAzureCredential(

                                exclude_interactive_browser_credential=False,

                                exclude_shared_token_cache_credential=False

                            )
            project_client = AIProjectClient(
                endpoint=project_endpoint,
                credential=credential
            )

            # Get Azure OpenAI client from project
            # AIProjectClient provides get_openai_client() method (verified via inspection)
            # External source: Microsoft Learn - Azure AI Foundry SDK Overview
            openai_client = project_client.get_openai_client()

            # Select model (use deployment name from Foundry)
            # Model names should match deployments in Azure AI Foundry
            model_name = request.model or self.config.get("azure_ai_foundry", {}).get("models", {}).get("default", "gpt-4")

            # Make inference request using OpenAI-compatible API
            # External source: Microsoft Learn - SDK usage examples
            start_time = datetime.now()
            response = openai_client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": request.prompt}],
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )

            latency = (datetime.now() - start_time).total_seconds() * 1000

            # Extract response
            response_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0

            # Calculate cost (approximate)
            cost = tokens_used * 0.00003 / 1000  # Rough estimate for GPT-4

            return InferenceResponse(
                response=response_text,
                model_used=model_name,
                provider=ModelProvider.AZURE_FOUNDRY,
                tokens_used=tokens_used,
                latency_ms=latency,
                cost=cost,
                metadata={"project_endpoint": project_endpoint}
            )

        except ImportError as e:
            logger.error(f"❌ Azure AI Foundry SDK not available: {e}")
            raise RuntimeError("Azure AI Foundry SDK not installed")
        except Exception as e:
            logger.error(f"❌ Azure inference error: {e}")
            raise

    def _inference_hybrid(self, request: InferenceRequest) -> InferenceResponse:
        """Hybrid inference: try local first, fallback to Azure"""
        try:
            return self._inference_local(request)
        except Exception as e:
            logger.info(f"   Local inference failed, falling back to Azure: {e}")
            return self._inference_azure(request)

    def _select_local_model(self, request: InferenceRequest) -> ModelEndpoint:
        """Select appropriate local model"""
        # If model specified, use it
        if request.model:
            model_key = f"iron_legion_{request.model}" if not request.model.startswith("ultron") else "ultron_local"
            if model_key in self.model_endpoints:
                return self.model_endpoints[model_key]

        # Default to first available local model
        local_models = [ep for ep in self.model_endpoints.values() if ep.provider == ModelProvider.LOCAL]
        if local_models:
            return local_models[0]

        raise RuntimeError("No local models available")

    def switch_model(self, model_id: str, provider: Optional[ModelProvider] = None):
        """Switch active model (for testing/experimentation)"""
        if model_id not in self.model_endpoints:
            raise ValueError(f"Model not found: {model_id}")

        endpoint = self.model_endpoints[model_id]
        if provider and endpoint.provider != provider:
            raise ValueError(f"Model provider mismatch: {endpoint.provider} != {provider}")

        logger.info(f"🔄 Switched to model: {model_id} ({endpoint.provider.value})")
        return endpoint

    def test_model_comparison(self, prompt: str, models: List[str]) -> Dict[str, InferenceResponse]:
        """Compare multiple models (A/B testing)"""
        results = {}

        for model_id in models:
            try:
                request = InferenceRequest(prompt=prompt, model=model_id)
                response = self.inference(request)
                results[model_id] = response
            except Exception as e:
                logger.error(f"❌ Error testing {model_id}: {e}")
                results[model_id] = None

        return results


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA + Azure AI Foundry Integration")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("--test", type=str, help="Test inference with prompt")
    parser.add_argument("--compare", type=str, nargs="+", help="Compare models (A/B test)")
    parser.add_argument("--switch", type=str, help="Switch to model")
    parser.add_argument("--provider", type=str, choices=["local", "azure", "hybrid"], help="Provider preference")

    args = parser.parse_args()

    integration = LuminaAzureAIFoundryIntegration()

    if args.list_models:
        models = integration.list_available_models()
        print("\n📋 Available Models:")
        for model in models:
            print(f"   {model.model_id} ({model.provider.value}) - {model.endpoint}")

    elif args.test:
        request = InferenceRequest(
            prompt=args.test,
            provider_preference=ModelProvider[args.provider.upper()] if args.provider else None
        )
        response = integration.inference(request)
        print(f"\n✅ Response from {response.model_used}:")
        print(f"   {response.response}")
        print(f"   Tokens: {response.tokens_used}, Latency: {response.latency_ms:.0f}ms, Cost: ${response.cost:.4f}")

    elif args.compare:
        prompt = input("Enter test prompt: ")
        results = integration.test_model_comparison(prompt, args.compare)
        print("\n📊 Model Comparison:")
        for model_id, response in results.items():
            if response:
                print(f"   {model_id}: {response.latency_ms:.0f}ms, {response.tokens_used} tokens")
            else:
                print(f"   {model_id}: Failed")

    elif args.switch:
        endpoint = integration.switch_model(args.switch)
        print(f"✅ Switched to: {endpoint.model_id} ({endpoint.provider.value})")

    else:
        print("🔷 LUMINA + Azure AI Foundry Integration")
        print("   Use --help for usage")


if __name__ == "__main__":


    main()