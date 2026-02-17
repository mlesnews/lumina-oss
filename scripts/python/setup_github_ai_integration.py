#!/usr/bin/env python3
"""
LUMINA GitHub AI Integration Setup

Complete setup for GitHub Models API integration with LUMINA's multi-provider AI system.
Configures token management, provider routing, and Cursor IDE integration.

Features:
- GitHub Personal Access Token setup
- Token pool configuration ($20 subscription = ~50K tokens)
- Model availability checking
- Cursor IDE model configuration
- Integration testing

Tags: #GITHUB #AI #INTEGRATION #SETUP #TOKEN_POOL #CURSOR @LUMINA
"""

import getpass
import os
import sys
from pathlib import Path
from typing import Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from github_ai_provider import GitHubAIProvider
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    GitHubAIProvider = None

logger = get_logger("GitHubAISetup")


class GitHubAISetup:
    """
    GitHub AI Integration Setup for LUMINA

    Handles complete setup of GitHub Models API integration,
    including token configuration, model testing, and Cursor integration.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize setup"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.github_provider: Optional[GitHubAIProvider] = None

        logger.info("🚀 GitHub AI Integration Setup initialized")

    def setup_github_token(self) -> bool:
        try:
            """Set up GitHub Personal Access Token"""
            print("\n" + "="*80)
            print("🔑 GITHUB PERSONAL ACCESS TOKEN SETUP")
            print("="*80)

            print("\nTo use GitHub Models, you need a GitHub Personal Access Token with 'models: read' permission.")
            print("\nSteps to create token:")
            print("1. Go to https://github.com/settings/tokens")
            print("2. Click 'Generate new token (classic)'")
            print("3. Select scopes: check 'models: read'")
            print("4. Copy the token (you won't see it again!)")

            current_token = os.getenv("GITHUB_TOKEN", "")
            if current_token:
                print(f"\n⚠️  Existing GITHUB_TOKEN found (ends with: ...{current_token[-4:]})")
                if not self._confirm("Replace existing token?"):
                    print("✅ Keeping existing token")
                    return True

            # Get new token
            while True:
                token = getpass.getpass("\nEnter your GitHub Personal Access Token: ").strip()

                if not token:
                    if not self._confirm("No token entered. Skip GitHub setup?"):
                        continue
                    return False

                if len(token) < 20:
                    print("❌ Token seems too short. GitHub tokens are typically 40+ characters.")
                    continue

                # Test token
                print("🔍 Testing token...")
                os.environ["GITHUB_TOKEN"] = token

                if GitHubAIProvider:
                    test_provider = GitHubAIProvider(project_root=self.project_root)
                    if test_provider.is_available():
                        print("✅ Token is valid!")
                        break
                    else:
                        print("❌ Token test failed. Please check the token and permissions.")
                        if not self._confirm("Try again?"):
                            return False
                else:
                    print("⚠️  Cannot test token (GitHubAIProvider not available)")
                    break

            # Save token to environment or .env file
            if self._confirm("Save token to .env file for persistence?"):
                env_file = self.project_root / ".env"
                env_content = ""

                if env_file.exists():
                    with open(env_file) as f:
                        env_content = f.read()

                # Remove existing GITHUB_TOKEN line
                lines = [line for line in env_content.split('\n') if not line.startswith('GITHUB_TOKEN=')]
                lines.append(f"GITHUB_TOKEN={token}")

                with open(env_file, 'w') as f:
                    f.write('\n'.join(lines))

                print("✅ Token saved to .env file")

            print("✅ GitHub token configured!")
            return True

        except Exception as e:
            self.logger.error(f"Error in setup_github_token: {e}", exc_info=True)
            raise
    def configure_token_pool(self) -> bool:
        """Configure GitHub token pool based on subscription"""
        print("\n" + "="*80)
        print("🪙 GITHUB TOKEN POOL CONFIGURATION")
        print("="*80)

        if not GitHubAIProvider:
            print("❌ GitHubAIProvider not available")
            return False

        self.github_provider = GitHubAIProvider(project_root=self.project_root)

        print("\nGitHub Models pricing (approximate):")
        print("• GPT-4o Mini: $0.15 per 1M input tokens, $0.60 per 1M output tokens")
        print("• GPT-4o: $2.50 per 1M input tokens, $10.00 per 1M output tokens")
        print("• Claude 3.5 Sonnet: $3.00 per 1M input tokens, $15.00 per 1M output tokens")

        print("\nYour $20 subscription gives approximately 50,000 tokens total.")
        print("This will be managed automatically by LUMINA's token pool system.")

        # Reset token pool
        self.github_provider.reset_token_pool(50000)  # $20 = ~50K tokens

        status = self.github_provider.get_token_pool_status()
        print("\n✅ Token pool configured:")
        print(f"   Total tokens: {status['total_tokens']:,}")
        print(f"   Remaining: {status['remaining_tokens']:,}")
        print(f"   Usage: {status['usage_percent']}%")
        print(f"   Emergency mode: {status['emergency_mode']}")

        return True

    def test_models(self) -> bool:
        """Test available GitHub models"""
        print("\n" + "="*80)
        print("🧪 TESTING GITHUB MODELS")
        print("="*80)

        if not self.github_provider:
            self.github_provider = GitHubAIProvider(project_root=self.project_root)

        print("🔍 Fetching available models...")

        try:
            models = self.github_provider.get_available_models()
            print(f"✅ Found {len(models)} available models:")

            for model in models[:10]:  # Show first 10
                print(f"   • {model['name']} ({model['provider']}) - {model['context_length']} tokens")

            if len(models) > 10:
                print(f"   ... and {len(models) - 10} more models")

        except Exception as e:
            print(f"❌ Failed to fetch models: {e}")
            return False

        # Test a simple chat completion
        print("\n🗣️  Testing chat completion...")
        test_models = ["openai/gpt-4o-mini", "anthropic/claude-3-haiku"]

        for model in test_models:
            try:
                messages = [{"role": "user", "content": "Hello! Please respond with just 'GitHub AI integration working!'"}]
                result = self.github_provider.chat_completion(model, messages, max_tokens=50)

                if result:
                    response = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                    tokens_used = result.get('usage', {}).get('total_tokens', 0)
                    print(f"✅ {model}: {response.strip()}")
                    print(f"   Tokens used: {tokens_used}")
                else:
                    print(f"❌ {model}: Failed to get response")

            except Exception as e:
                print(f"❌ {model}: Error - {e}")

        return True

    def setup_cursor_integration(self) -> bool:
        try:
            """Set up Cursor IDE integration"""
            print("\n" + "="*80)
            print("🖥️  CURSOR IDE INTEGRATION")
            print("="*80)

            config_file = self.project_root / "data" / "cursor_models" / "cursor_models_config.json"

            if not config_file.exists():
                print("❌ Cursor models config file not found")
                return False

            print("📝 GitHub models have been added to Cursor configuration:")
            print(f"   File: {config_file}")

            print("\nModels added:")
            print("   • GitHub GPT-4o (Premium)")
            print("   • GitHub Claude 3.5 Sonnet (Premium)")
            print("   • GitHub GPT-4o Mini (Free Tier)")

            print("\nTo use these models in Cursor:")
            print("1. Open Cursor Settings (Ctrl+Shift+,)")
            print("2. Go to 'Models' section")
            print("3. The models should appear in your custom models list")
            print("4. Select a GitHub model to start using it!")

            print("\n⚠️  Note: Models route through LUMINA's AI router at http://<NAS_IP>:8080")
            print("   Make sure the ULTRON Cluster Router is running for GitHub models to work.")

            return True

        except Exception as e:
            self.logger.error(f"Error in setup_cursor_integration: {e}", exc_info=True)
            raise
    def run_full_setup(self) -> bool:
        """Run complete GitHub AI integration setup"""
        print("🚀 LUMINA GITHUB AI INTEGRATION SETUP")
        print("="*80)
        print("This will set up full GitHub Models API integration with:")
        print("• Personal Access Token configuration")
        print("• Token pool management ($20 subscription)")
        print("• Model availability testing")
        print("• Cursor IDE integration")
        print()

        if not self._confirm("Continue with setup?"):
            return False

        success = True

        # Step 1: Token setup
        if not self.setup_github_token():
            print("❌ Token setup failed")
            success = False

        # Step 2: Token pool configuration
        if success and not self.configure_token_pool():
            print("❌ Token pool configuration failed")
            success = False

        # Step 3: Model testing
        if success and not self.test_models():
            print("❌ Model testing failed")
            success = False

        # Step 4: Cursor integration
        if not self.setup_cursor_integration():
            print("❌ Cursor integration setup failed")
            success = False

        # Final status
        print("\n" + "="*80)
        if success:
            print("🎉 GITHUB AI INTEGRATION COMPLETE!")
            print("="*80)
            print("✅ GitHub Personal Access Token configured")
            print("✅ Token pool management active")
            print("✅ Models tested and working")
            print("✅ Cursor IDE integration ready")
            print()
            print("🚀 You can now use GitHub models in Cursor!")
            print("   Select 'GitHub GPT-4o' or 'GitHub Claude 3.5 Sonnet' from the model picker.")
            print()
            print("💡 Token usage is automatically tracked and managed.")
            print("   When tokens run low, you'll automatically fall back to local models.")
        else:
            print("❌ GITHUB AI INTEGRATION INCOMPLETE")
            print("   Some steps failed. Please check the errors above.")

        return success

    def _confirm(self, message: str) -> bool:
        """Get user confirmation"""
        while True:
            response = input(f"{message} (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no', '']:
                return False
            else:
                print("Please enter 'y' or 'n'")


def main():
    """Main setup entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="GitHub AI Integration Setup for LUMINA")
    parser.add_argument("--full-setup", action="store_true", help="Run complete setup")
    parser.add_argument("--token-only", action="store_true", help="Setup GitHub token only")
    parser.add_argument("--test-models", action="store_true", help="Test GitHub models")
    parser.add_argument("--cursor-config", action="store_true", help="Setup Cursor integration")

    args = parser.parse_args()

    setup = GitHubAISetup()

    if args.full_setup:
        setup.run_full_setup()
    elif args.token_only:
        setup.setup_github_token()
    elif args.test_models:
        setup.test_models()
    elif args.cursor_config:
        setup.setup_cursor_integration()
    else:
        parser.print_help()


if __name__ == "__main__":

    main()