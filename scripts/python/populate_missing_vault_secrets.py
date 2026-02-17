#!/usr/bin/env python3
"""
Populate Missing Vault Secrets

Interactive script to add all missing API keys to Azure Key Vault.
NO SECRETS IN THE CLEAR! 🔐

Usage:
    python populate_missing_vault_secrets.py
    python populate_missing_vault_secrets.py --check-only
    python populate_missing_vault_secrets.py --add openai-api-key

Tags: #SECURITY #AZURE_KEY_VAULT @JARVIS @fullauto
"""

import sys
import os
import getpass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
logger = logging.getLogger("populate_missing_vault_secrets")


# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class SecretConfig:
    """Configuration for a secret"""
    name: str
    env_var: str
    description: str
    example: str
    provider_url: str


# All secrets that should be in the vault
REQUIRED_SECRETS: Dict[str, SecretConfig] = {
    "openai-api-key": SecretConfig(
        name="openai-api-key",
        env_var="OPENAI_API_KEY",
        description="OpenAI API (GPT-4, GPT-4o, etc.)",
        example="sk-proj-xxx...",
        provider_url="https://platform.openai.com/api-keys"
    ),
    "anthropic-api-key": SecretConfig(
        name="anthropic-api-key",
        env_var="ANTHROPIC_API_KEY",
        description="Anthropic API (Claude 3.5, Claude 4)",
        example="sk-ant-xxx...",
        provider_url="https://console.anthropic.com/settings/keys"
    ),
    "azure-openai-api-key": SecretConfig(
        name="azure-openai-api-key",
        env_var="AZURE_OPENAI_API_KEY",
        description="Azure OpenAI Service",
        example="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        provider_url="https://portal.azure.com (Cognitive Services)"
    ),
    "google-ai-api-key": SecretConfig(
        name="google-ai-api-key",
        env_var="GOOGLE_AI_API_KEY",
        description="Google AI (Gemini)",
        example="AIzaSy...",
        provider_url="https://aistudio.google.com/app/apikey"
    ),
    "elevenlabs-api-key": SecretConfig(
        name="elevenlabs-api-key",
        env_var="ELEVENLABS_API_KEY",
        description="ElevenLabs Text-to-Speech",
        example="sk_...",
        provider_url="https://elevenlabs.io/app/settings/api-keys"
    ),
    "github-token": SecretConfig(
        name="github-token",
        env_var="GITHUB_TOKEN",
        description="GitHub Personal Access Token",
        example="ghp_xxxx...",
        provider_url="https://github.com/settings/tokens"
    ),
    "deepseek-api-key": SecretConfig(
        name="deepseek-api-key",
        env_var="DEEPSEEK_API_KEY",
        description="DeepSeek API",
        example="sk-...",
        provider_url="https://platform.deepseek.com/api_keys"
    ),
    "mistral-api-key": SecretConfig(
        name="mistral-api-key",
        env_var="MISTRAL_API_KEY",
        description="Mistral AI API",
        example="...",
        provider_url="https://console.mistral.ai/api-keys/"
    ),
    "groq-api-key": SecretConfig(
        name="groq-api-key",
        env_var="GROQ_API_KEY",
        description="Groq API (fast inference)",
        example="gsk_...",
        provider_url="https://console.groq.com/keys"
    ),
    "xai-api-key": SecretConfig(
        name="xai-api-key",
        env_var="XAI_API_KEY",
        description="xAI API (Grok)",
        example="xai-...",
        provider_url="https://console.x.ai/"
    ),
    "openrouter-api-key": SecretConfig(
        name="openrouter-api-key",
        env_var="OPENROUTER_API_KEY",
        description="OpenRouter API (multi-model)",
        example="sk-or-...",
        provider_url="https://openrouter.ai/keys"
    ),
    "together-api-key": SecretConfig(
        name="together-api-key",
        env_var="TOGETHER_API_KEY",
        description="Together AI API",
        example="...",
        provider_url="https://api.together.xyz/settings/api-keys"
    ),
}


VAULT_URL = "https://jarvis-lumina.vault.azure.net/"


def get_vault_client():
    """Get Azure Key Vault client"""
    try:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient

        credential = DefaultAzureCredential(


                            exclude_interactive_browser_credential=False,


                            exclude_shared_token_cache_credential=False


                        )
        return SecretClient(vault_url=VAULT_URL, credential=credential)
    except ImportError:
        print("ERROR: Azure SDK not installed.")
        print("Run: pip install azure-identity azure-keyvault-secrets")
        sys.exit(1)


def check_existing_secrets() -> Tuple[List[str], List[str]]:
    """Check which secrets exist and which are missing"""
    client = get_vault_client()

    existing = []
    missing = []

    print("\n" + "="*70)
    print("🔐 CHECKING AZURE KEY VAULT SECRETS")
    print(f"   Vault: {VAULT_URL}")
    print("="*70 + "\n")

    # Get all secrets in vault
    vault_secrets = {s.name for s in client.list_properties_of_secrets()}

    for name, config in REQUIRED_SECRETS.items():
        if name in vault_secrets:
            existing.append(name)
            print(f"  ✅ {name} ({config.description})")
        else:
            missing.append(name)
            print(f"  ❌ {name} ({config.description})")

    return existing, missing


def add_secret_to_vault(name: str, value: str) -> bool:
    """Add a secret to the vault"""
    client = get_vault_client()

    try:
        config = REQUIRED_SECRETS.get(name)
        description = config.description if config else "Custom secret"

        client.set_secret(
            name,
            value,
            content_type="text/plain",
            tags={
                "service": name.replace("-api-key", "").replace("-", "_"),
                "managed_by": "lumina",
                "description": description
            }
        )
        return True
    except Exception as e:
        print(f"ERROR: Could not add secret: {e}")
        return False


def prompt_for_secret(config: SecretConfig) -> Optional[str]:
    """Prompt user for a secret value"""
    print(f"\n{'─'*70}")
    print(f"  📝 {config.name}")
    print(f"     {config.description}")
    print(f"     Example: {config.example}")
    print(f"     Get key: {config.provider_url}")
    print(f"{'─'*70}")

    value = getpass.getpass(f"  Enter API key (or press Enter to skip): ")

    if value and len(value) > 5:
        return value
    return None


def set_environment_variable(env_var: str, value: str):
    """Set environment variable for current session"""
    os.environ[env_var] = value
    print(f"  → Set {env_var} for current session")


def interactive_add_missing(missing: List[str]) -> int:
    """Interactively add missing secrets"""
    if not missing:
        print("\n✅ All required secrets are already in the vault!")
        return 0

    print(f"\n{'='*70}")
    print(f"🔐 ADD MISSING SECRETS ({len(missing)} to configure)")
    print(f"{'='*70}")

    added = 0
    skipped = 0

    for name in missing:
        config = REQUIRED_SECRETS.get(name)
        if not config:
            continue

        value = prompt_for_secret(config)

        if value:
            if add_secret_to_vault(name, value):
                masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"  ✅ Added {name} to vault ({masked})")
                set_environment_variable(config.env_var, value)
                added += 1
            else:
                print(f"  ❌ Failed to add {name}")
        else:
            print(f"  ⏭️  Skipped {name}")
            skipped += 1

    print(f"\n{'='*70}")
    print(f"📊 SUMMARY")
    print(f"   Added: {added}")
    print(f"   Skipped: {skipped}")
    print(f"{'='*70}\n")

    return added


def run_startup_refresh():
    try:
        """Run the startup script to refresh environment variables"""
        print("\n🔄 Refreshing environment variables from vault...")

        startup_script = project_root / "scripts" / "startup" / "lumina_secure_startup.ps1"
        if startup_script.exists():
            import subprocess
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(startup_script)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✅ Environment variables refreshed!")
            else:
                print(f"⚠️  Startup script returned: {result.returncode}")
        else:
            print("⚠️  Startup script not found")


    except Exception as e:
        logger.error(f"Error in run_startup_refresh: {e}", exc_info=True)
        raise
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Populate missing vault secrets")
    parser.add_argument('--check-only', action='store_true', help='Only check, do not add')
    parser.add_argument('--add', type=str, help='Add specific secret by name')
    parser.add_argument('--refresh', action='store_true', help='Refresh env vars after')

    args = parser.parse_args()

    print("\n" + "🔐"*35)
    print("       LUMINA VAULT SECRET MANAGER")
    print("       NO SECRETS IN THE CLEAR!")
    print("🔐"*35)

    # Check existing
    existing, missing = check_existing_secrets()

    print(f"\n📊 Status: {len(existing)} configured, {len(missing)} missing")

    if args.check_only:
        if missing:
            print("\n⚠️  Missing secrets:")
            for name in missing:
                config = REQUIRED_SECRETS.get(name)
                if config:
                    print(f"   - {name}: {config.provider_url}")
        return 0 if not missing else 1

    if args.add:
        # Add specific secret
        if args.add not in REQUIRED_SECRETS:
            print(f"ERROR: Unknown secret '{args.add}'")
            print("Known secrets:", ", ".join(REQUIRED_SECRETS.keys()))
            return 1

        config = REQUIRED_SECRETS[args.add]
        value = prompt_for_secret(config)
        if value:
            if add_secret_to_vault(args.add, value):
                print(f"✅ Added {args.add} to vault!")
                set_environment_variable(config.env_var, value)
            else:
                print(f"❌ Failed to add {args.add}")
                return 1
    else:
        # Interactive mode
        added = interactive_add_missing(missing)

        if added > 0 or args.refresh:
            run_startup_refresh()

    print("\n✅ Complete! Run 'python scripts/startup/lumina_secure_startup.ps1' to refresh all env vars.\n")
    return 0


if __name__ == "__main__":


    sys.exit(main())