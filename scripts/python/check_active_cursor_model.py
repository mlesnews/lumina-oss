#!/usr/bin/env python3
"""
Check Active Cursor Model
Helps identify which AI model is currently active in Cursor IDE

This script:
1. Checks Ollama local endpoints for active models
2. Monitors network activity (if possible)
3. Provides model identification assistance
4. Helps verify local vs cloud model usage
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CheckActiveCursorModel")


class CursorModelChecker:
    """Check which AI model is active in Cursor"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(".").resolve()
        self.config_dir = self.project_root / "config"

        # Endpoints to check
        self.local_endpoints = [
            "http://localhost:11434",
            "http://localhost:11437",
            "http://<NAS_PRIMARY_IP>:11437",  # KAIJU
            "http://kaiju_no_8:11437",
        ]

    def check_ollama_endpoints(self) -> Dict[str, Any]:
        """Check which Ollama endpoints are active"""
        results = {}

        for endpoint in self.local_endpoints:
            try:
                response = requests.get(f"{endpoint}/api/tags", timeout=2)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [m.get("name", "unknown") for m in models]
                    results[endpoint] = {
                        "status": "active",
                        "models": model_names,
                        "count": len(model_names)
                    }
                else:
                    results[endpoint] = {
                        "status": "error",
                        "code": response.status_code
                    }
            except requests.exceptions.RequestException as e:
                results[endpoint] = {
                    "status": "unreachable",
                    "error": str(e)
                }

        return results

    def get_expected_models(self) -> Dict[str, List[str]]:
        """Get expected models from configuration"""
        expected = {
            "ULTRON": ["qwen2.5:72b", "llama3.2:3b"],
            "IRON_LEGION": [
                "codellama:13b",
                "llama3.2:11b",
                "qwen2.5-coder:1.5b-base",
                "llama3",
                "mistral",
                "mixtral-8x7b",
                "gemma:2b"
            ]
        }

        # Try to load from config files
        try:
            ultron_config = self.config_dir / "cursor_ultron_model_config.json"
            if ultron_config.exists():
                with open(ultron_config) as f:
                    config = json.load(f)
                    # Extract model info if available
                    pass
        except Exception as e:
            logger.debug(f"Could not load ULTRON config: {e}")

        return expected

    def generate_model_identification_prompt(self) -> str:
        """Generate a prompt to ask the model to identify itself"""
        prompts = [
            "What model are you? Please identify your name and version.",
            "Please tell me: What AI model are you?",
            "Identify yourself: What is your model name?",
            "What language model is responding to this message?",
        ]
        return prompts[0]  # Use first prompt

    def check_cursor_settings(self) -> Dict[str, Any]:
        """Check Cursor settings for model configuration"""
        settings_file = self.project_root / ".cursor" / "settings.json"
        settings = {}

        if settings_file.exists():
            try:
                with open(settings_file) as f:
                    cursor_settings = json.load(f)

                    settings = {
                        "default_model_chat": cursor_settings.get("cursor.chat.defaultModel"),
                        "default_model_composer": cursor_settings.get("cursor.composer.defaultModel"),
                        "default_model_agent": cursor_settings.get("cursor.agent.defaultModel"),
                        "ollama_endpoint": cursor_settings.get("ollama.endpoint"),
                        "ollama_default_model": cursor_settings.get("ollama.defaultModel"),
                        "custom_models": cursor_settings.get("cursor.chat.customModels", []),
                    }
            except Exception as e:
                logger.error(f"Error reading Cursor settings: {e}")
        else:
            logger.warning(f"Cursor settings file not found: {settings_file}")

        return settings

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive model status report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "ollama_endpoints": self.check_ollama_endpoints(),
            "cursor_settings": self.check_cursor_settings(),
            "expected_models": self.get_expected_models(),
            "identification_prompt": self.generate_model_identification_prompt(),
            "recommendations": []
        }

        # Analyze and add recommendations
        active_endpoints = [ep for ep, status in report["ollama_endpoints"].items() 
                           if status.get("status") == "active"]

        if not active_endpoints:
            report["recommendations"].append(
                "⚠️  No local Ollama endpoints active. Check if Ollama is running."
            )

        default_model = report["cursor_settings"].get("default_model_chat")
        if default_model and default_model not in ["ULTRON", "ollama", "local"]:
            report["recommendations"].append(
                f"⚠️  Default chat model is '{default_model}'. Verify it's a local model."
            )

        return report

    def print_report(self, report: Dict[str, Any]):
        """Print human-readable report"""
        print("\n" + "="*70)
        print("CURSOR ACTIVE MODEL CHECKER")
        print("="*70)
        print(f"\nTimestamp: {report['timestamp']}")

        print("\n📡 Ollama Endpoints Status:")
        print("-" * 70)
        for endpoint, status in report["ollama_endpoints"].items():
            if status.get("status") == "active":
                models = status.get("models", [])
                print(f"✅ {endpoint}")
                print(f"   Models ({status.get('count', 0)}): {', '.join(models[:3])}")
                if len(models) > 3:
                    print(f"   ... and {len(models) - 3} more")
            elif status.get("status") == "error":
                print(f"❌ {endpoint} - Error {status.get('code')}")
            else:
                print(f"⚪ {endpoint} - {status.get('status', 'unknown')}")

        print("\n⚙️  Cursor Settings:")
        print("-" * 70)
        settings = report["cursor_settings"]
        if settings:
            print(f"Chat Default Model: {settings.get('default_model_chat', 'Not set')}")
            print(f"Composer Default: {settings.get('default_model_composer', 'Not set')}")
            print(f"Agent Default: {settings.get('default_model_agent', 'Not set')}")
            print(f"Ollama Endpoint: {settings.get('ollama_endpoint', 'Not set')}")
            print(f"Ollama Default Model: {settings.get('ollama_default_model', 'Not set')}")
            if settings.get("custom_models"):
                print(f"Custom Models: {len(settings['custom_models'])} configured")
        else:
            print("⚠️  Cursor settings not found")

        if report.get("recommendations"):
            print("\n💡 Recommendations:")
            print("-" * 70)
            for rec in report["recommendations"]:
                print(f"  {rec}")

        print("\n🔍 Model Identification Prompt:")
        print("-" * 70)
        print(f"Ask in Cursor Chat: \"{report['identification_prompt']}\"")
        print("\nThis will help identify which model is actually responding.")

        print("\n" + "="*70)
        print("NOTE: This script checks LOCAL endpoints only.")
        print("To verify CLOUD model usage, check Anthropic/OpenAI dashboards.")
        print("="*70 + "\n")


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Check active AI model in Cursor IDE"
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output as JSON"
        )
        parser.add_argument(
            "--save",
            type=Path,
            help="Save report to file"
        )

        args = parser.parse_args()

        checker = CursorModelChecker()
        report = checker.generate_report()

        if args.json:
            print(json.dumps(report, indent=2))
        else:
            checker.print_report(report)

        if args.save:
            args.save.parent.mkdir(parents=True, exist_ok=True)
            with open(args.save, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n✅ Report saved to: {args.save}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()