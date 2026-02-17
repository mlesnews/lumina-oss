#!/usr/bin/env python3
"""
List All AI Services and Models Installed

Comprehensive list of all AI services, models, and configurations available on this laptop.

Tags: #AI #SERVICES #LIST #INVENTORY @JARVIS @LUMINA
"""

import sys
import json
import subprocess
import os
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ListAllAIServices")


class AIServiceInventory:
    """
    Comprehensive AI Service Inventory

    Lists all AI services, models, and configurations
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize AI service inventory"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"

        self.inventory = {
            "timestamp": datetime.now().isoformat(),
            "local_ai": {},
            "cloud_ai": {},
            "installed_models": [],
            "running_services": [],
            "configuration_files": []
        }

        logger.info("✅ AI Service Inventory initialized")

    def check_ollama(self) -> Dict[str, Any]:
        """Check Ollama installation and models"""
        logger.info("🔍 Checking Ollama...")

        ollama_info = {
            "installed": False,
            "running": False,
            "port": 11434,
            "url": "http://localhost:11434",
            "models": [],
            "processes": []
        }

        # Check if Ollama is installed
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                ollama_info["installed"] = True
                # Parse models from output
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 1:
                            model_name = parts[0]
                            model_size = parts[2] if len(parts) > 2 else "Unknown"
                            ollama_info["models"].append({
                                "name": model_name,
                                "size": model_size
                            })
        except FileNotFoundError:
            logger.debug("   Ollama command not found")
        except Exception as e:
            logger.debug(f"   Error checking Ollama: {e}")

        # Check if Ollama is running
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if 'ollama' in proc.info['name'].lower():
                        ollama_info["running"] = True
                        ollama_info["processes"].append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "path": proc.info.get('exe', 'Unknown')
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            logger.debug("   psutil not available")
        except Exception as e:
            logger.debug(f"   Error checking processes: {e}")

        # Check if Ollama API is accessible
        try:
            response = requests.get(f"{ollama_info['url']}/api/tags", timeout=5)
            if response.status_code == 200:
                ollama_info["api_accessible"] = True
                api_models = response.json().get("models", [])
                if api_models:
                    ollama_info["api_models"] = [
                        {
                            "name": m.get("name", ""),
                            "size": m.get("size", 0),
                            "modified": m.get("modified_at", "")
                        }
                        for m in api_models
                    ]
        except Exception as e:
            ollama_info["api_accessible"] = False
            logger.debug(f"   Ollama API not accessible: {e}")

        if ollama_info["installed"] or ollama_info["running"]:
            logger.info(f"   ✅ Ollama found: {len(ollama_info['models'])} models")

        return ollama_info

    def check_ultron_kaiju(self) -> Dict[str, Any]:
        """Check ULTRON and KAIJU configurations"""
        logger.info("🔍 Checking ULTRON and KAIJU...")

        ultron_kaiju = {
            "ultron": {
                "configured": False,
                "url": os.getenv("ULTRON_URL", "http://localhost:11434"),
                "available": False
            },
            "kaiju": {
                "configured": False,
                "url": os.getenv("KAIJU_URL", "http://<NAS_IP>:11434"),
                "available": False
            }
        }

        # Check ULTRON
        ultron_url = os.getenv("ULTRON_URL", "http://localhost:11434")
        ultron_kaiju["ultron"]["configured"] = bool(os.getenv("ULTRON_URL"))
        ultron_kaiju["ultron"]["url"] = ultron_url

        try:
            response = requests.get(f"{ultron_url}/api/tags", timeout=5)
            if response.status_code == 200:
                ultron_kaiju["ultron"]["available"] = True
                logger.info(f"   ✅ ULTRON available at {ultron_url}")
        except Exception as e:
            logger.debug(f"   ULTRON not available: {e}")

        # Check KAIJU
        kaiju_url = os.getenv("KAIJU_URL", "http://<NAS_IP>:11434")
        ultron_kaiju["kaiju"]["configured"] = bool(os.getenv("KAIJU_URL"))
        ultron_kaiju["kaiju"]["url"] = kaiju_url

        try:
            response = requests.get(f"{kaiju_url}/api/tags", timeout=5)
            if response.status_code == 200:
                ultron_kaiju["kaiju"]["available"] = True
                logger.info(f"   ✅ KAIJU available at {kaiju_url}")
        except Exception as e:
            logger.debug(f"   KAIJU not available: {e}")

        return ultron_kaiju

    def check_cloud_ai(self) -> Dict[str, Any]:
        """Check cloud AI service configurations"""
        logger.info("🔍 Checking Cloud AI Services...")

        cloud_ai = {
            "aws_bedrock": {
                "configured": False,
                "available": False,
                "region": os.getenv("AWS_REGION"),
                "has_credentials": bool(os.getenv("AWS_ACCESS_KEY_ID"))
            },
            "azure_openai": {
                "configured": False,
                "available": False,
                "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
                "has_key": bool(os.getenv("AZURE_OPENAI_API_KEY"))
            },
            "anthropic": {
                "configured": False,
                "available": False,
                "has_key": bool(os.getenv("ANTHROPIC_API_KEY"))
            },
            "openai": {
                "configured": False,
                "available": False,
                "has_key": bool(os.getenv("OPENAI_API_KEY"))
            }
        }

        # AWS Bedrock
        if os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_REGION"):
            cloud_ai["aws_bedrock"]["configured"] = True
            logger.info("   ✅ AWS Bedrock configured")

        # Azure OpenAI
        if os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_ENDPOINT"):
            cloud_ai["azure_openai"]["configured"] = True
            logger.info("   ✅ Azure OpenAI configured")

        # Anthropic
        if os.getenv("ANTHROPIC_API_KEY"):
            cloud_ai["anthropic"]["configured"] = True
            logger.info("   ✅ Anthropic API configured")

        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            cloud_ai["openai"]["configured"] = True
            logger.info("   ✅ OpenAI API configured")

        return cloud_ai

    def check_config_files(self) -> List[Dict[str, Any]]:
        """Check AI configuration files"""
        logger.info("🔍 Checking Configuration Files...")

        config_files = []
        ai_config_patterns = [
            "**/*ai*config*.json",
            "**/*ollama*.json",
            "**/*ultron*.json",
            "**/*kaiju*.json",
            "**/*bedrock*.json",
            "**/*openai*.json"
        ]

        for pattern in ai_config_patterns:
            for config_file in self.config_dir.glob(pattern):
                try:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                    config_files.append({
                        "path": str(config_file.relative_to(self.project_root)),
                        "size": config_file.stat().st_size,
                        "modified": datetime.fromtimestamp(config_file.stat().st_mtime).isoformat()
                    })
                except Exception:
                    pass

        logger.info(f"   Found {len(config_files)} AI configuration files")
        return config_files

    def generate_inventory(self) -> Dict[str, Any]:
        """Generate complete AI service inventory"""
        logger.info("=" * 80)
        logger.info("📋 Generating AI Service Inventory")
        logger.info("=" * 80)
        logger.info("")

        # Check Ollama
        self.inventory["local_ai"]["ollama"] = self.check_ollama()
        logger.info("")

        # Check ULTRON/KAIJU
        self.inventory["local_ai"]["ultron_kaiju"] = self.check_ultron_kaiju()
        logger.info("")

        # Check Cloud AI
        self.inventory["cloud_ai"] = self.check_cloud_ai()
        logger.info("")

        # Check config files
        self.inventory["configuration_files"] = self.check_config_files()
        logger.info("")

        # Summary
        total_models = len(self.inventory["local_ai"].get("ollama", {}).get("models", []))
        total_services = sum([
            1 for service in self.inventory["cloud_ai"].values() if service.get("configured", False)
        ])

        logger.info("=" * 80)
        logger.info("📊 INVENTORY SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Local AI Models: {total_models}")
        logger.info(f"Cloud AI Services: {total_services}")
        logger.info(f"Configuration Files: {len(self.inventory['configuration_files'])}")
        logger.info("=" * 80)

        return self.inventory

    def print_inventory(self):
        """Print human-readable inventory"""
        print("\n" + "=" * 80)
        print("🤖 AI SERVICES INVENTORY")
        print("=" * 80)
        print()

        # Local AI
        print("📍 LOCAL AI SERVICES:")
        print("-" * 80)

        ollama = self.inventory["local_ai"].get("ollama", {})
        if ollama.get("installed") or ollama.get("running"):
            status = "✅ RUNNING" if ollama.get("running") else "⚠️  INSTALLED"
            print(f"Ollama: {status}")
            print(f"  URL: {ollama.get('url', 'N/A')}")
            print(f"  API Accessible: {'✅' if ollama.get('api_accessible') else '❌'}")
            print(f"  Models Installed: {len(ollama.get('models', []))}")
            for model in ollama.get("models", []):
                print(f"    - {model.get('name', 'Unknown')} ({model.get('size', 'Unknown')})")
        else:
            print("Ollama: ❌ NOT INSTALLED")

        print()

        ultron_kaiju = self.inventory["local_ai"].get("ultron_kaiju", {})
        ultron = ultron_kaiju.get("ultron", {})
        kaiju = ultron_kaiju.get("kaiju", {})

        print(f"ULTRON: {'✅' if ultron.get('available') else '❌'} ({ultron.get('url', 'N/A')})")
        print(f"KAIJU: {'✅' if kaiju.get('available') else '❌'} ({kaiju.get('url', 'N/A')})")

        print()

        # Cloud AI
        print("☁️  CLOUD AI SERVICES:")
        print("-" * 80)

        cloud_ai = self.inventory["cloud_ai"]
        for service_name, service_info in cloud_ai.items():
            status = "✅ CONFIGURED" if service_info.get("configured") else "❌ NOT CONFIGURED"
            print(f"{service_name.replace('_', ' ').title()}: {status}")
            if service_info.get("configured"):
                if service_info.get("region"):
                    print(f"  Region: {service_info['region']}")
                if service_info.get("endpoint"):
                    print(f"  Endpoint: {service_info['endpoint']}")

        print()

        # Configuration Files
        if self.inventory["configuration_files"]:
            print("📁 CONFIGURATION FILES:")
            print("-" * 80)
            for config_file in self.inventory["configuration_files"][:10]:  # Show first 10
                print(f"  - {config_file['path']}")
            if len(self.inventory["configuration_files"]) > 10:
                print(f"  ... and {len(self.inventory['configuration_files']) - 10} more")

        print()
        print("=" * 80)


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="List All AI Services and Models")
        parser.add_argument("--json", action="store_true", help="Output as JSON")
        parser.add_argument("--save", metavar="FILE", help="Save inventory to file")

        args = parser.parse_args()

        inventory = AIServiceInventory()
        result = inventory.generate_inventory()

        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            inventory.print_inventory()

        if args.save:
            with open(args.save, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"✅ Inventory saved to: {args.save}")
        else:
            # Save default
            default_file = inventory.project_root / "data" / "ai_service_inventory" / f"inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            default_file.parent.mkdir(parents=True, exist_ok=True)
            with open(default_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"✅ Inventory saved to: {default_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()