#!/usr/bin/env python3
"""
Export API Keys to Cursor Models Section

Retrieves API keys from Azure Key Vault and generates
Cursor-compatible model configurations.

Tags: #API_KEYS #CURSOR #AZURE_KEY_VAULT @JARVIS @TEAM
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import logging

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ExportAPIKeysToCursor")


@dataclass
class CursorModelConfig:
    """Cursor model configuration"""
    title: str
    name: str
    provider: str
    model: str
    apiKey: Optional[str] = None  # Will be populated from vault
    apiBase: Optional[str] = None
    contextLength: int = 32768
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        result = {}
        for k, v in asdict(self).items():
            if v is not None:
                result[k] = v
        return result


# Define known AI providers and their expected secret names in Azure Key Vault
AI_PROVIDERS = {
    "openai": {
        "vault_secret": "openai-api-key",
        "env_var": "OPENAI_API_KEY",
        "models": [
            CursorModelConfig(
                title="OpenAI GPT-4o",
                name="gpt-4o",
                provider="openai",
                model="gpt-4o",
                contextLength=128000,
                description="Latest GPT-4o model"
            ),
            CursorModelConfig(
                title="OpenAI GPT-4o Mini",
                name="gpt-4o-mini",
                provider="openai",
                model="gpt-4o-mini",
                contextLength=128000,
                description="Fast, cost-effective GPT-4o Mini"
            ),
            CursorModelConfig(
                title="OpenAI o1",
                name="o1",
                provider="openai",
                model="o1",
                contextLength=128000,
                description="OpenAI o1 reasoning model"
            ),
            CursorModelConfig(
                title="OpenAI o1-mini",
                name="o1-mini",
                provider="openai",
                model="o1-mini",
                contextLength=128000,
                description="OpenAI o1-mini reasoning model"
            ),
        ]
    },
    "anthropic": {
        "vault_secret": "anthropic-api-key",
        "env_var": "ANTHROPIC_API_KEY",
        "models": [
            CursorModelConfig(
                title="Claude Opus 4",
                name="claude-opus-4-20250514",
                provider="anthropic",
                model="claude-opus-4-20250514",
                contextLength=200000,
                description="Claude Opus 4 - Most capable"
            ),
            CursorModelConfig(
                title="Claude Sonnet 4",
                name="claude-sonnet-4-20250514",
                provider="anthropic",
                model="claude-sonnet-4-20250514",
                contextLength=200000,
                description="Claude Sonnet 4 - Balanced"
            ),
            CursorModelConfig(
                title="Claude 3.5 Sonnet",
                name="claude-3-5-sonnet-20241022",
                provider="anthropic",
                model="claude-3-5-sonnet-20241022",
                contextLength=200000,
                description="Claude 3.5 Sonnet - Fast & capable"
            ),
        ]
    },
    "azure_openai": {
        "vault_secret": "azure-openai-api-key",
        "env_var": "AZURE_OPENAI_API_KEY",
        "endpoint_env": "AZURE_OPENAI_ENDPOINT",
        "models": [
            CursorModelConfig(
                title="Azure GPT-4",
                name="azure-gpt-4",
                provider="azure",
                model="gpt-4",
                contextLength=128000,
                description="Azure OpenAI GPT-4"
            ),
            CursorModelConfig(
                title="Azure GPT-4 Turbo",
                name="azure-gpt-4-turbo",
                provider="azure",
                model="gpt-4-turbo",
                contextLength=128000,
                description="Azure OpenAI GPT-4 Turbo"
            ),
        ]
    },
    "google": {
        "vault_secret": "google-ai-api-key",
        "env_var": "GOOGLE_AI_API_KEY",
        "models": [
            CursorModelConfig(
                title="Gemini 2.0 Flash",
                name="gemini-2.0-flash",
                provider="google",
                model="gemini-2.0-flash",
                contextLength=1000000,
                description="Google Gemini 2.0 Flash"
            ),
            CursorModelConfig(
                title="Gemini Pro",
                name="gemini-pro",
                provider="google",
                model="gemini-pro",
                contextLength=32768,
                description="Google Gemini Pro"
            ),
        ]
    },
    "xai": {
        "vault_secret": "xai-api-key",
        "env_var": "XAI_API_KEY",
        "models": [
            CursorModelConfig(
                title="Grok 2",
                name="grok-2",
                provider="xai",
                model="grok-2",
                contextLength=131072,
                description="xAI Grok 2"
            ),
        ]
    },
    "deepseek": {
        "vault_secret": "deepseek-api-key",
        "env_var": "DEEPSEEK_API_KEY",
        "models": [
            CursorModelConfig(
                title="DeepSeek V3",
                name="deepseek-v3",
                provider="deepseek",
                model="deepseek-chat",
                apiBase="https://api.deepseek.com/v1",
                contextLength=65536,
                description="DeepSeek V3 - Amazing for code"
            ),
            CursorModelConfig(
                title="DeepSeek R1",
                name="deepseek-r1",
                provider="deepseek",
                model="deepseek-reasoner",
                apiBase="https://api.deepseek.com/v1",
                contextLength=65536,
                description="DeepSeek R1 - Reasoning model"
            ),
        ]
    },
    "mistral": {
        "vault_secret": "mistral-api-key",
        "env_var": "MISTRAL_API_KEY",
        "models": [
            CursorModelConfig(
                title="Mistral Large",
                name="mistral-large",
                provider="mistral",
                model="mistral-large-latest",
                contextLength=32768,
                description="Mistral Large"
            ),
            CursorModelConfig(
                title="Codestral",
                name="codestral",
                provider="mistral",
                model="codestral-latest",
                contextLength=32768,
                description="Mistral Codestral - Optimized for code"
            ),
        ]
    },
    "groq": {
        "vault_secret": "groq-api-key",
        "env_var": "GROQ_API_KEY",
        "models": [
            CursorModelConfig(
                title="Groq Llama 3.3 70B",
                name="groq-llama-3.3-70b",
                provider="groq",
                model="llama-3.3-70b-versatile",
                apiBase="https://api.groq.com/openai/v1",
                contextLength=128000,
                description="Groq Llama 3.3 70B - Ultra fast"
            ),
        ]
    },
    "together": {
        "vault_secret": "together-api-key",
        "env_var": "TOGETHER_API_KEY",
        "models": [
            CursorModelConfig(
                title="Together Llama 3.3 70B",
                name="together-llama-3.3-70b",
                provider="together",
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
                apiBase="https://api.together.xyz/v1",
                contextLength=128000,
                description="Together AI Llama 3.3 70B"
            ),
        ]
    },
    "openrouter": {
        "vault_secret": "openrouter-api-key",
        "env_var": "OPENROUTER_API_KEY",
        "models": [
            CursorModelConfig(
                title="OpenRouter (Multi-model)",
                name="openrouter",
                provider="openrouter",
                model="openai/gpt-4o",
                apiBase="https://openrouter.ai/api/v1",
                contextLength=128000,
                description="OpenRouter - GPT-4o via OpenRouter (supports image input, reliable model selection)"
            ),
        ]
    },
    "elevenlabs": {
        "vault_secret": "elevenlabs-api-key",
        "env_var": "ELEVENLABS_API_KEY",
        "models": []  # TTS, not LLM
    },
}


class APIKeyExporter:
    """Export API keys to Cursor models configuration"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.output_dir = self.project_root / "data" / "cursor_models"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Try to get keys from Azure Key Vault
        self.vault_available = False
        self.vault_client = None
        self._init_vault()

        logger.info("✅ API Key Exporter initialized")

    def _init_vault(self):
        """Initialize Azure Key Vault client"""
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient

            vault_url = "https://jarvis-lumina.vault.azure.net/"
            credential = DefaultAzureCredential(

                                exclude_interactive_browser_credential=False,

                                exclude_shared_token_cache_credential=False

                            )
            self.vault_client = SecretClient(vault_url=vault_url, credential=credential)
            self.vault_available = True
            logger.info("✅ Azure Key Vault client initialized")
        except ImportError:
            logger.warning("⚠️  Azure SDK not installed. Using environment variables only.")
        except Exception as e:
            logger.warning(f"⚠️  Could not connect to Azure Key Vault: {e}")

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for provider from vault or env"""
        provider_config = AI_PROVIDERS.get(provider)
        if not provider_config:
            return None

        # Try Azure Key Vault first
        if self.vault_available and self.vault_client:
            try:
                secret_name = provider_config.get("vault_secret")
                if secret_name:
                    secret = self.vault_client.get_secret(secret_name)
                    if secret and secret.value:
                        logger.info(f"   ✅ Got {provider} key from Azure Key Vault")
                        return secret.value
            except Exception as e:
                logger.debug(f"   Could not get {provider} from vault: {e}")

        # Fallback to environment variable
        env_var = provider_config.get("env_var")
        if env_var:
            key = os.environ.get(env_var)
            if key:
                logger.info(f"   ✅ Got {provider} key from environment variable")
                return key

        return None

    def generate_cursor_models_config(self, include_keys: bool = False) -> Dict[str, Any]:
        """Generate Cursor models configuration"""
        logger.info("="*80)
        logger.info("🔧 Generating Cursor Models Configuration")
        logger.info("="*80)

        models = []
        providers_found = []
        providers_missing = []

        for provider_name, provider_config in AI_PROVIDERS.items():
            provider_models = provider_config.get("models", [])
            if not provider_models:
                continue

            api_key = self.get_api_key(provider_name) if include_keys else None

            if api_key or not include_keys:
                if api_key:
                    providers_found.append(provider_name)
                for model in provider_models:
                    model_config = model.to_dict()
                    if include_keys and api_key:
                        model_config["apiKey"] = api_key
                    models.append(model_config)
                    logger.info(f"   📦 Added: {model.title}")
            else:
                providers_missing.append(provider_name)
                logger.info(f"   ⚠️  Skipped {provider_name} (no API key found)")

        # Add local ULTRON models (no API key needed)
        local_models = [
            {
                "title": "ULTRON (Local)",
                "name": "ultron-local",
                "provider": "ollama",
                "model": "qwen2.5:72b",
                "apiBase": "http://localhost:11434",
                "contextLength": 32768,
                "description": "Local ULTRON - No cloud API needed",
                "localOnly": True
            },
            {
                "title": "KAIJU (Iron Legion)",
                "name": "kaiju",
                "provider": "ollama",
                "model": "llama3.2:3b",
                "apiBase": "http://<NAS_PRIMARY_IP>:11434",
                "contextLength": 8192,
                "description": "KAIJU NAS - 7 Iron Legion models",
                "localOnly": True
            },
        ]
        models.extend(local_models)

        result = {
            "cursor.chat.customModels": models,
            "cursor.composer.customModels": models,
            "providers_found": providers_found,
            "providers_missing": providers_missing,
            "total_models": len(models),
            "instructions": {
                "step1": "Open Cursor Settings (Ctrl+Shift+,)",
                "step2": "Go to 'Models' section",
                "step3": "Click 'Add Model' and paste each model config",
                "step4": "Or copy the entire JSON to settings.json"
            }
        }

        logger.info("="*80)
        logger.info(f"✅ Generated {len(models)} model configurations")
        logger.info(f"   Providers with keys: {len(providers_found)}")
        logger.info(f"   Providers missing keys: {len(providers_missing)}")
        logger.info("="*80)

        return result

    def export_to_file(self, include_keys: bool = False) -> Path:
        try:
            """Export configuration to file"""
            config = self.generate_cursor_models_config(include_keys=include_keys)

            # Save full config (for reference)
            output_file = self.output_dir / "cursor_models_config.json"
            with open(output_file, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info(f"✅ Saved to: {output_file}")

            # Save a safe version (without keys) for documentation
            safe_config = self.generate_cursor_models_config(include_keys=False)
            safe_file = self.output_dir / "cursor_models_config_template.json"
            with open(safe_file, 'w') as f:
                json.dump(safe_config, f, indent=2)

            logger.info(f"✅ Template saved to: {safe_file}")

            return output_file

        except Exception as e:
            self.logger.error(f"Error in export_to_file: {e}", exc_info=True)
            raise
    def print_setup_instructions(self):
        """Print setup instructions for adding models to Cursor"""
        print("\n" + "="*80)
        print("📋 HOW TO ADD API KEYS TO CURSOR MODELS SECTION")
        print("="*80)
        print("""
METHOD 1: Via Cursor Settings UI
--------------------------------
1. Open Cursor Settings: Ctrl+Shift+, (or Cmd+Shift+, on Mac)
2. Search for 'Models'
3. Scroll to 'Custom Models' section
4. Click 'Add Model' for each provider

METHOD 2: Via settings.json
---------------------------
1. Open Command Palette: Ctrl+Shift+P
2. Type: 'Preferences: Open User Settings (JSON)'
3. Add the models from the generated config file

API KEYS NEEDED:
""")
        for provider, config in AI_PROVIDERS.items():
            if config.get("models"):
                env_var = config.get("env_var", "N/A")
                print(f"  • {provider.upper()}: {env_var}")

        print("""
WHERE TO GET API KEYS:
  • OpenAI: https://platform.openai.com/api-keys
  • Anthropic: https://console.anthropic.com/settings/keys
  • Azure: https://portal.azure.com (Azure OpenAI resource)
  • Google: https://aistudio.google.com/apikey
  • xAI: https://console.x.ai/
  • DeepSeek: https://platform.deepseek.com/api-keys
  • Mistral: https://console.mistral.ai/api-keys
  • Groq: https://console.groq.com/keys
  • Together: https://api.together.xyz/settings/api-keys
  • OpenRouter: https://openrouter.ai/keys

YOUR AZURE KEY VAULT:
  • Vault: https://jarvis-lumina.vault.azure.net/
  • Add secrets with names like: openai-api-key, anthropic-api-key, etc.
""")
        print("="*80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Export API Keys to Cursor Models")
    parser.add_argument('--include-keys', action='store_true',
                       help='Include actual API keys in output (use with caution!)')
    parser.add_argument('--instructions', action='store_true',
                       help='Print setup instructions')
    parser.add_argument('--list-providers', action='store_true',
                       help='List all supported providers')

    args = parser.parse_args()

    exporter = APIKeyExporter()

    if args.instructions:
        exporter.print_setup_instructions()
        return 0

    if args.list_providers:
        print("\n📋 Supported AI Providers:")
        for provider, config in AI_PROVIDERS.items():
            models = config.get("models", [])
            if models:
                print(f"\n  {provider.upper()}:")
                for m in models:
                    print(f"    • {m.title} ({m.model})")
        return 0

    # Default: export config
    output_file = exporter.export_to_file(include_keys=args.include_keys)
    exporter.print_setup_instructions()

    print(f"\n✅ Configuration saved to: {output_file}")
    return 0


if __name__ == "__main__":


    sys.exit(main())