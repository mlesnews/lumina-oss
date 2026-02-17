#!/usr/bin/env python3
"""
Configure Local AI with R5 Lattice Escalation
Prefers local models, escalates to cloud AI via R5 decisioning lattice when needed

Tags: #AI #LOCAL_AI #R5 #LATTICE #ESCALATION #DECISIONING
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("LocalAIR5Escalation")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("LocalAIR5Escalation")

try:
    from unified_secrets_manager import UnifiedSecretsManager, SecretSource
    SECRETS_AVAILABLE = True
except ImportError:
    SECRETS_AVAILABLE = False
    logger.warning("UnifiedSecretsManager not available")


class LocalAIR5EscalationConfig:
    """Configure local AI with R5 lattice escalation to cloud"""

    def __init__(self, project_root: Path):
        """Initialize configuration"""
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.secrets_manager = None
        if SECRETS_AVAILABLE:
            try:
                self.secrets_manager = UnifiedSecretsManager(self.project_root)
                logger.info("✅ Unified Secrets Manager initialized")
            except Exception as e:
                logger.warning(f"⚠️  Secrets Manager not available: {e}")

        logger.info("✅ Local AI with R5 Escalation Config initialized")

    def check_cloud_ai_fallback(self) -> Dict[str, Any]:
        """Check if cloud AI credentials exist for fallback"""
        logger.info("🔍 Checking cloud AI fallback credentials...")

        status = {
            "openai": {"available": False},
            "anthropic": {"available": False},
            "azure_openai": {"available": False}
        }

        if not self.secrets_manager:
            return status

        # Check OpenAI
        openai_key = self.secrets_manager.get_secret(
            "openai-api-key",
            source=SecretSource.AZURE_KEY_VAULT
        ) or self.secrets_manager.get_secret(
            "OPENAI_API_KEY",
            source=SecretSource.AZURE_KEY_VAULT
        )

        if openai_key:
            status["openai"]["available"] = True
            status["openai"]["key_length"] = len(openai_key)

        # Check Anthropic
        anthropic_key = self.secrets_manager.get_secret(
            "anthropic-api-key",
            source=SecretSource.AZURE_KEY_VAULT
        ) or self.secrets_manager.get_secret(
            "ANTHROPIC_API_KEY",
            source=SecretSource.AZURE_KEY_VAULT
        )

        if anthropic_key:
            status["anthropic"]["available"] = True
            status["anthropic"]["key_length"] = len(anthropic_key)

        # Check Azure OpenAI
        azure_key = self.secrets_manager.get_secret(
            "azure-openai-api-key",
            source=SecretSource.AZURE_KEY_VAULT
        )
        azure_endpoint = self.secrets_manager.get_secret(
            "azure-openai-endpoint",
            source=SecretSource.AZURE_KEY_VAULT
        )

        if azure_key and azure_endpoint:
            status["azure_openai"]["available"] = True

        return status

    def create_local_ai_r5_config(self) -> bool:
        """Create configuration for local AI with R5 escalation"""
        logger.info("📝 Creating local AI with R5 escalation config...")

        config_file = self.config_dir / "local_ai_r5_escalation_config.json"

        # Check what cloud AI is available for fallback
        cloud_status = self.check_cloud_ai_fallback()
        fallback_provider = None
        fallback_model = None

        if cloud_status["openai"]["available"]:
            fallback_provider = "openai"
            fallback_model = "gpt-4"
        elif cloud_status["anthropic"]["available"]:
            fallback_provider = "anthropic"
            fallback_model = "claude-3-opus-20240229"
        elif cloud_status["azure_openai"]["available"]:
            fallback_provider = "azure_openai"
            fallback_model = "gpt-4"

        config = {
            "version": "1.0.0",
            "name": "Local AI with R5 Lattice Escalation",
            "description": "Prefers local models, escalates to cloud via R5 decisioning lattice",
            "preference": "local_ai",
            "local_ai": {
                "enabled": True,
                "preferred": True,
                "primary": True,
                "models": {
                    "default": "llama3.2:11b",
                    "fallback": "codellama:13b",
                    "lightweight": "qwen2.5-coder:1.5b-base"
                },
                "base_url": "http://<NAS_IP>:3001",
                "load_balancer": "http://<NAS_IP>:3000"
            },
            "r5_escalation": {
                "enabled": True,
                "lattice_decisioning": True,
                "escalation_triggers": [
                    "local_model_failure",
                    "complexity_threshold_exceeded",
                    "confidence_below_threshold",
                    "timeout_exceeded",
                    "r5_decision_required"
                ],
                "r5_endpoint": "http://localhost:8000/r5",
                "decisioning_matrix": {
                    "use_r5_lattice": True,
                    "lattice_path": "r5_living_context_matrix",
                    "escalation_priority": "high"
                }
            },
            "aiq_quorum": {
                "enabled": True,
                "description": "AI Quorum achieved through Jedi Council and Jedi High Council",
                "jedi_council": {
                    "enabled": True,
                    "abbreviation": "JC",
                    "endpoint": "http://localhost:8000/jedi-council",
                    "requires_approval": True,
                    "use_for": [
                        "standard_aiq_consensus",
                        "moderate_complexity",
                        "multi_provider_quorum"
                    ]
                },
                "jedi_high_council": {
                    "enabled": True,
                    "abbreviation": "JHC",
                    "endpoint": "http://localhost:8000/jedi-high-council",
                    "requires_approval": True,
                    "use_for": [
                        "critical_decisions",
                        "high_complexity",
                        "final_escalation",
                        "cloud_ai_approval"
                    ]
                },
                "quorum_size": 3,
                "consensus_threshold": 0.7,
                "escalation_flow": [
                    "1. R5 Lattice evaluates complexity",
                    "2. If complex → AIQ Quorum requested",
                    "3. AIQ uses Jedi Council (JC) for consensus",
                    "4. If critical → Escalate to Jedi High Council (JHC)",
                    "5. JHC approves cloud AI escalation if needed"
                ]
            },
            "cloud_ai_fallback": {
                "enabled": fallback_provider is not None,
                "provider": fallback_provider,
                "model": fallback_model,
                "only_on_escalation": True,
                "requires_r5_approval": True,
                "requires_aiq_approval": True,
                "requires_jedi_high_council": True,
                "escalation_flow": [
                    "1. Try local AI",
                    "2. If fails/complex → R5 lattice evaluation",
                    "3. R5 decides: escalate to AIQ",
                    "4. AIQ uses Jedi Council (JC) for quorum",
                    "5. If critical → Jedi High Council (JHC) approval",
                    "6. JHC approves cloud AI escalation",
                    "7. Cloud AI handles complex decision",
                    "8. Return result"
                ]
            },
            "decisioning": {
                "primary": "local_ai",
                "escalation": "r5_lattice",
                "aiq_quorum": "jedi_council",
                "high_escalation": "jedi_high_council",
                "fallback": "cloud_ai",
                "temperature": 0.7,
                "max_tokens": 2000,
                "timeout": 30
            },
            "monitoring": {
                "track_local_usage": True,
                "track_escalations": True,
                "track_r5_decisions": True,
                "log_all_escalations": True
            }
        }

        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"✅ Local AI R5 config saved to: {config_file}")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving config: {e}")
            return False

    def update_aiq_fallback_for_r5(self) -> bool:
        """Update AIQ fallback to use R5 lattice escalation"""
        logger.info("🔄 Updating AIQ fallback for R5 lattice escalation...")

        aiq_file = self.project_root / "scripts" / "python" / "aiq_fallback_decisioning.py"

        if not aiq_file.exists():
            logger.warning("⚠️  AIQ fallback file not found")
            return False

        # Read current file
        try:
            content = aiq_file.read_text()

            # Check if R5 integration exists
            if "r5" in content.lower() and "lattice" in content.lower():
                logger.info("✅ AIQ fallback already has R5 lattice integration")
                return True

            logger.info("💡 AIQ fallback needs R5 lattice integration")
            logger.info("   See: docs/local_ai/R5_ESCALATION_INTEGRATION.md")
            return True

        except Exception as e:
            logger.error(f"❌ Error reading AIQ file: {e}")
            return False

    def setup_complete_r5_escalation(self) -> Dict[str, Any]:
        """Complete setup for local AI with R5 escalation"""
        logger.info("🚀 Setting up local AI with R5 lattice escalation...")

        results = {
            "config": False,
            "cloud_fallback": False,
            "aiq_update": False
        }

        # Step 1: Create config
        results["config"] = self.create_local_ai_r5_config()

        # Step 2: Check cloud fallback
        cloud_status = self.check_cloud_ai_fallback()
        results["cloud_fallback"] = any(
            provider["available"] 
            for provider in cloud_status.values()
        )

        if not results["cloud_fallback"]:
            logger.warning("⚠️  No cloud AI fallback configured")
            logger.info("   Local AI will be used exclusively")
            logger.info("   To add fallback: python scripts/python/configure_cloud_ai_decisioning.py --setup openai")

        # Step 3: Update AIQ
        results["aiq_update"] = self.update_aiq_fallback_for_r5()

        return results


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Configure Local AI with R5 Lattice Escalation"
    )
    parser.add_argument("--check", action="store_true", help="Check current configuration")
    parser.add_argument("--setup", action="store_true", help="Setup local AI with R5 escalation")

    args = parser.parse_args()

    config = LocalAIR5EscalationConfig(project_root)

    if args.check:
        cloud_status = config.check_cloud_ai_fallback()
        print("\n📊 Cloud AI Fallback Status:")
        print(f"   OpenAI: {'✅' if cloud_status['openai']['available'] else '❌'}")
        print(f"   Anthropic: {'✅' if cloud_status['anthropic']['available'] else '❌'}")
        print(f"   Azure OpenAI: {'✅' if cloud_status['azure_openai']['available'] else '❌'}")
        print("\n💡 Local AI is preferred, cloud AI only used via R5 escalation")

    elif args.setup:
        results = config.setup_complete_r5_escalation()

        print("\n" + "="*80)
        print("🚀 LOCAL AI WITH R5 ESCALATION SETUP")
        print("="*80)
        print(f"   Config: {'✅' if results['config'] else '❌'}")
        print(f"   Cloud Fallback: {'✅ Available' if results['cloud_fallback'] else '❌ Not Configured'}")
        print(f"   AIQ Update: {'✅' if results['aiq_update'] else '⚠️'}")
        print("\n📋 Configuration:")
        print("   • Local AI: PRIMARY (preferred)")
        print("   • R5 Lattice: ESCALATION (for complex decisions)")
        print("   • AIQ Quorum: JEDI COUNCIL (JC) for consensus")
        print("   • High Escalation: JEDI HIGH COUNCIL (JHC) for critical")
        print("   • Cloud AI: FALLBACK (only via R5 → AIQ → JHC approval)")
        print("\n💡 Next steps:")
        print("   1. Test local AI: python scripts/python/aiq_fallback_decisioning.py --check-load")
        print("   2. Review config: config/local_ai_r5_escalation_config.json")
        if not results['cloud_fallback']:
            print("   3. (Optional) Add cloud fallback for R5 escalation")

    else:
        parser.print_help()


if __name__ == "__main__":


    sys.exit(main() or 0)