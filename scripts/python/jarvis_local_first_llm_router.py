#!/usr/bin/env python3
"""
JARVIS Local-First LLM Router

ENFORCES LOCAL-FIRST AI RESOURCE USAGE:
- Primary: Local Ollama (laptop)
- Secondary: KAIJU Iron Legion (NAS)
- Tertiary: ULTRON Router (smart routing)
- LAST RESORT: Cloud APIs (only if all local fail)

This ensures we utilize local infrastructure before cloud resources.
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISLocalFirstLLM")


class LLMProvider(Enum):
    """LLM Provider types"""
    LOCAL_OLLAMA = "local_ollama"  # Local laptop Ollama
    KAIJU_IRON_LEGION = "kaiju_iron_legion"  # KAIJU NAS
    ULTRON_ROUTER = "ultron_router"  # ULTRON smart router
    ULTRON_LOCAL = "ultron_local"  # ULTRON local cluster
    CLOUD_ANTHROPIC = "cloud_anthropic"  # Cloud fallback
    AZURE_OPENAI = "azure_openai"  # Azure OpenAI Service (enforced for all OpenAI requests)
    CLOUD_OPENAI = "cloud_openai"  # DEPRECATED - Use AZURE_OPENAI instead
    CLOUD_CURSOR = "cloud_cursor"  # Cloud fallback


class JARVISLocalFirstLLMRouter:
    """
    Local-First LLM Router

    ENFORCES: Local resources FIRST, cloud LAST
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Load configuration
        self.config = self._load_config()

        # Initialize @DOIT Local-First AI Policy
        try:
            from doit_local_first_ai_policy import DOITLocalFirstAIPolicy
            self.ai_policy = DOITLocalFirstAIPolicy(project_root)
            self.logger.info("✅ @DOIT Local-First AI Policy integrated")
        except ImportError:
            self.ai_policy = None
            self.logger.warning("⚠️  @DOIT Local-First AI Policy not available")

        # Provider endpoints (LOCAL FIRST)
        self.providers = {
            LLMProvider.LOCAL_OLLAMA: {
                "base_url": "http://localhost:11434",
                "enabled": True,
                "priority": 1,
                "models": ["qwen2.5:72b", "llama3.2:11b", "codellama:13b"]
            },
            LLMProvider.KAIJU_IRON_LEGION: {
                "base_url": "http://<NAS_PRIMARY_IP>:11434",
                "enabled": True,
                "priority": 2,
                "models": ["llama3", "codellama:13b"]
            },
            LLMProvider.ULTRON_ROUTER: {
                "base_url": "http://<NAS_PRIMARY_IP>:3008",
                "enabled": True,
                "priority": 3,
                "models": ["qwen2.5:72b"]
            },
            LLMProvider.ULTRON_LOCAL: {
                "base_url": "http://localhost:11434",
                "enabled": True,
                "priority": 4,
                "models": ["qwen2.5:72b"]
            },
            # CLOUD PROVIDERS - LAST RESORT ONLY
            LLMProvider.AZURE_OPENAI: {
                "base_url": self._get_azure_openai_endpoint(),
                "api_version": "2024-02-15-preview",
                "enabled": self.config.get("cloud_fallback_enabled", False),
                "priority": 98,
                "requires_approval": True,
                "azure_deployment": self._get_azure_openai_deployment()
            },
            LLMProvider.CLOUD_ANTHROPIC: {
                "base_url": "https://api.anthropic.com",
                "enabled": self.config.get("cloud_fallback_enabled", False),
                "priority": 99,  # Very low priority
                "requires_approval": True
            },
            LLMProvider.CLOUD_OPENAI: {
                "base_url": "https://api.openai.com",
                "enabled": False,  # DEPRECATED - Use AZURE_OPENAI instead. All OpenAI requests MUST route through Azure.
                "priority": 999,  # Disabled - blocked
                "requires_approval": True,
                "deprecated": True,
                "replacement": "AZURE_OPENAI"
            },
            LLMProvider.CLOUD_CURSOR: {
                "base_url": "https://api.cursor.com",
                "enabled": self.config.get("cloud_fallback_enabled", False),
                "priority": 97,
                "requires_approval": True
            }
        }

        # Health status
        self.provider_health: Dict[LLMProvider, bool] = {}
        self.last_health_check = None

        # Usage statistics
        self.usage_stats = {
            "local_requests": 0,
            "kaiju_requests": 0,
            "ultron_requests": 0,
            "cloud_requests": 0,
            "total_requests": 0
        }

        # Check health on init
        self._check_all_providers_health()

        self.logger.info("✅ JARVIS Local-First LLM Router initialized")
        self.logger.info(f"   Local providers: {sum(1 for p in self.providers.values() if p['priority'] < 10)}")
        self.logger.info(f"   Cloud fallback: {'ENABLED' if self.config.get('cloud_fallback_enabled', False) else 'DISABLED'}")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        config_file = self.project_root / "config" / "local_first_llm_config.json"

        default_config = {
            "cloud_fallback_enabled": False,  # DISABLED by default
            "require_approval_for_cloud": True,
            "preferred_model": "qwen2.5:72b",
            "timeout": 30,
            "max_retries": 3
        }

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to load config: {e}, using defaults")
        else:
            # Save default config
            try:
                config_file.parent.mkdir(parents=True, exist_ok=True)
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2)
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to save default config: {e}")

        return default_config

    def _load_azure_openai_config(self) -> Dict[str, Any]:
        """Load Azure OpenAI configuration"""
        config_file = self.project_root / "config" / "azure_openai_config.json"

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to load Azure OpenAI config: {e}")

        return {}

    def _get_azure_openai_endpoint(self) -> str:
        """Get Azure OpenAI endpoint from config or environment"""
        import os
        azure_config = self._load_azure_openai_config()

        # Try config first
        resource_name = azure_config.get("azure_openai", {}).get("resource_name", "")
        if resource_name and not resource_name.startswith("${"):
            endpoint_template = azure_config.get("azure_openai", {}).get("endpoint_template", 
                "https://{resource_name}.openai.azure.com")
            return endpoint_template.format(resource_name=resource_name)

        # Fallback to environment variable
        resource_name = os.getenv("AZURE_OPENAI_RESOURCE_NAME", "")
        if resource_name:
            return f"https://{resource_name}.openai.azure.com"

        # Default/placeholder (will fail if not configured)
        self.logger.warning("⚠️  Azure OpenAI resource name not configured. Set AZURE_OPENAI_RESOURCE_NAME or configure azure_openai_config.json")
        return "https://YOUR-RESOURCE-NAME.openai.azure.com"

    def _get_azure_openai_deployment(self) -> str:
        """Get Azure OpenAI deployment name from config or environment"""
        import os
        azure_config = self._load_azure_openai_config()

        # Try config first
        deployment = azure_config.get("azure_openai", {}).get("deployment_name", "")
        if deployment and not deployment.startswith("${"):
            return deployment

        # Try default deployment
        deployments = azure_config.get("azure_openai", {}).get("deployments", {})
        default_deployment = deployments.get("default", {}).get("name", "")
        if default_deployment and not default_deployment.startswith("${"):
            return default_deployment

        # Fallback to environment variable
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        return deployment

    def _check_provider_health(self, provider: LLMProvider) -> bool:
        """Check if a provider is healthy"""
        provider_config = self.providers.get(provider)
        if not provider_config or not provider_config.get("enabled"):
            return False

        base_url = provider_config["base_url"]

        try:
            # For Ollama, check /api/tags endpoint
            if "ollama" in base_url or "localhost" in base_url or "<NAS_PRIMARY_IP>" in base_url:
                response = requests.get(f"{base_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    return True

            # For cloud APIs, we'd check differently
            # For now, assume cloud is available if enabled
            if provider in [LLMProvider.CLOUD_ANTHROPIC, LLMProvider.AZURE_OPENAI, LLMProvider.CLOUD_OPENAI, LLMProvider.CLOUD_CURSOR]:
                return provider_config.get("enabled", False)

            return False
        except Exception as e:
            self.logger.debug(f"Provider {provider.value} health check failed: {e}")
            return False

    def _check_all_providers_health(self):
        """Check health of all providers"""
        self.logger.info("🔍 Checking local LLM provider health...")

        for provider in LLMProvider:
            is_healthy = self._check_provider_health(provider)
            self.provider_health[provider] = is_healthy

            if is_healthy:
                priority = self.providers[provider]["priority"]
                if priority < 10:
                    self.logger.info(f"   ✅ {provider.value} - HEALTHY (Priority: {priority})")
                else:
                    self.logger.info(f"   ⚠️  {provider.value} - Available (Cloud fallback)")
            else:
                if self.providers[provider].get("priority", 99) < 10:
                    self.logger.warning(f"   ❌ {provider.value} - UNAVAILABLE")

        self.last_health_check = datetime.now()

    def get_available_providers(self, include_cloud: bool = False) -> List[LLMProvider]:
        """
        Get list of available providers, ordered by priority (LOCAL FIRST)

        Args:
            include_cloud: Include cloud providers (default: False)
        """
        available = []

        for provider in LLMProvider:
            # Skip cloud unless explicitly requested
            if not include_cloud and provider.value.startswith("cloud_"):
                continue

            if self.provider_health.get(provider, False):
                available.append(provider)

        # Sort by priority
        available.sort(key=lambda p: self.providers[p]["priority"])

        return available

    def route_request(self, prompt: str, model: Optional[str] = None, 
                     allow_cloud: bool = False) -> Dict[str, Any]:
        """
        Route LLM request to best available provider (LOCAL FIRST)

        Policy: Use @local @ai @llm @agent resources over cloud AI providers,
        unless @bau #decisioning @r5 @matrix/@lattice approves cloud usage.

        Args:
            prompt: The prompt to send
            model: Specific model to use (optional)
            allow_cloud: Allow cloud fallback (default: False) - requires policy approval

        Returns:
            Dict with response and provider used
        """
        self.logger.info(f"📤 Routing LLM request (allow_cloud={allow_cloud})...")

        # Check if cloud is requested - enforce @DOIT Local-First AI Policy
        if allow_cloud and self.ai_policy:
            # Check if cloud model is requested
            is_cloud = self.ai_policy._is_cloud_provider(model) if model else False

            if is_cloud:
                # Get policy approval for cloud usage
                decision = self.ai_policy.decide_ai_provider(
                    task_description=f"LLM request: {prompt[:100]}",
                    context={"prompt": prompt, "model": model},
                    requested_provider=model
                )

                if not decision.use_cloud:
                    # Cloud not approved - use local instead
                    self.logger.warning(f"🚫 Cloud provider blocked by policy: {model}")
                    self.logger.info(f"   ✅ Using local AI instead: {decision.approved_provider.value}")
                    allow_cloud = False  # Override to use local
                else:
                    # Cloud approved
                    self.logger.info(f"✅ Cloud provider approved by {decision.decisioning_source}: {model}")

        # Get available providers
        available = self.get_available_providers(include_cloud=allow_cloud)

        if not available:
            self.logger.error("❌ No LLM providers available!")
            return {
                "success": False,
                "error": "No LLM providers available",
                "provider": None
            }

        # Try providers in priority order (LOCAL FIRST)
        for provider in available:
            try:
                self.logger.info(f"   Trying {provider.value} (Priority: {self.providers[provider]['priority']})...")

                result = self._send_request(provider, prompt, model)

                if result["success"]:
                    # Update usage stats
                    if provider == LLMProvider.LOCAL_OLLAMA or provider == LLMProvider.ULTRON_LOCAL:
                        self.usage_stats["local_requests"] += 1
                    elif provider == LLMProvider.KAIJU_IRON_LEGION:
                        self.usage_stats["kaiju_requests"] += 1
                    elif provider in [LLMProvider.ULTRON_ROUTER]:
                        self.usage_stats["ultron_requests"] += 1
                    else:
                        self.usage_stats["cloud_requests"] += 1

                    self.usage_stats["total_requests"] += 1

                    self.logger.info(f"   ✅ Success with {provider.value}")
                    return result
                else:
                    self.logger.warning(f"   ⚠️  {provider.value} failed: {result.get('error')}")

            except Exception as e:
                self.logger.error(f"   ❌ Error with {provider.value}: {e}")
                continue

        # All providers failed
        self.logger.error("❌ All LLM providers failed!")
        return {
            "success": False,
            "error": "All LLM providers failed",
            "provider": None
        }

    def _send_request(self, provider: LLMProvider, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Send request to specific provider"""
        provider_config = self.providers[provider]
        base_url = provider_config["base_url"]

        # Select model
        if not model:
            model = provider_config.get("models", [None])[0] or self.config.get("preferred_model", "qwen2.5:72b")

        # For Ollama providers
        if provider in [LLMProvider.LOCAL_OLLAMA, LLMProvider.KAIJU_IRON_LEGION, 
                       LLMProvider.ULTRON_ROUTER, LLMProvider.ULTRON_LOCAL]:
            try:
                response = requests.post(
                    f"{base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=self.config.get("timeout", 30)
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "provider": provider.value,
                        "response": data.get("response", ""),
                        "model": model,
                        "base_url": base_url
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text}",
                        "provider": provider.value
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "provider": provider.value
                }

        # For cloud providers (would need API keys)
        elif provider in [LLMProvider.CLOUD_ANTHROPIC, LLMProvider.AZURE_OPENAI, LLMProvider.CLOUD_OPENAI, LLMProvider.CLOUD_CURSOR]:
            # Cloud provider implementation would go here
            # Note: AZURE_OPENAI is the preferred provider for OpenAI requests
            # CLOUD_OPENAI is deprecated and disabled
            if provider == LLMProvider.CLOUD_OPENAI:
                return {
                    "success": False,
                    "error": "Direct OpenAI access is blocked. Use AZURE_OPENAI instead.",
                    "provider": provider.value,
                    "suggestion": "Use LLMProvider.AZURE_OPENAI instead"
                }
            return {
                "success": False,
                "error": "Cloud providers disabled (local-first policy)",
                "provider": provider.value
            }

        return {
            "success": False,
            "error": "Unknown provider type",
            "provider": provider.value
        }

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        total = self.usage_stats["total_requests"]

        stats = {
            "total_requests": total,
            "local_requests": self.usage_stats["local_requests"],
            "kaiju_requests": self.usage_stats["kaiju_requests"],
            "ultron_requests": self.usage_stats["ultron_requests"],
            "cloud_requests": self.usage_stats["cloud_requests"],
            "local_percentage": (self.usage_stats["local_requests"] / total * 100) if total > 0 else 0,
            "kaiju_percentage": (self.usage_stats["kaiju_requests"] / total * 100) if total > 0 else 0,
            "cloud_percentage": (self.usage_stats["cloud_requests"] / total * 100) if total > 0 else 0
        }

        return stats

    def force_local_only(self):
        """Force local-only mode (disable cloud completely)"""
        self.config["cloud_fallback_enabled"] = False
        for provider in [LLMProvider.CLOUD_ANTHROPIC, LLMProvider.AZURE_OPENAI, LLMProvider.CLOUD_OPENAI, LLMProvider.CLOUD_CURSOR]:
            self.providers[provider]["enabled"] = False

        self.logger.warning("🔒 LOCAL-ONLY MODE ENABLED - Cloud providers disabled")


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Local-First LLM Router")
        parser.add_argument("--health", action="store_true", help="Check provider health")
        parser.add_argument("--stats", action="store_true", help="Show usage statistics")
        parser.add_argument("--test", type=str, help="Test with a prompt")
        parser.add_argument("--force-local", action="store_true", help="Force local-only mode")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        router = JARVISLocalFirstLLMRouter(project_root)

        if args.force_local:
            router.force_local_only()
            print("✅ Local-only mode enabled")

        elif args.health:
            router._check_all_providers_health()
            print("\n📊 Provider Status:")
            for provider, healthy in router.provider_health.items():
                status = "✅ HEALTHY" if healthy else "❌ UNAVAILABLE"
                priority = router.providers[provider]["priority"]
                print(f"   {provider.value}: {status} (Priority: {priority})")

        elif args.stats:
            stats = router.get_usage_stats()
            print("\n📊 Usage Statistics:")
            print(f"   Total Requests: {stats['total_requests']}")
            print(f"   Local: {stats['local_requests']} ({stats['local_percentage']:.1f}%)")
            print(f"   KAIJU: {stats['kaiju_requests']} ({stats['kaiju_percentage']:.1f}%)")
            print(f"   ULTRON: {stats['ultron_requests']} ({stats.get('ultron_percentage', 0):.1f}%)")
            print(f"   Cloud: {stats['cloud_requests']} ({stats['cloud_percentage']:.1f}%)")

        elif args.test:
            result = router.route_request(args.test, allow_cloud=False)
            if result["success"]:
                print(f"\n✅ Response from {result['provider']}:")
                print(result["response"][:500])
            else:
                print(f"\n❌ Error: {result.get('error')}")

        else:
            print("Usage:")
            print("  --health          : Check provider health")
            print("  --stats           : Show usage statistics")
            print("  --test 'prompt'   : Test with a prompt")
            print("  --force-local     : Force local-only mode")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()