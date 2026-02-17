#!/usr/bin/env python3
"""
Validate Ollama model configuration against actual server inventory.
RR Methodology: Rest, Roast, Repair - Model Validation Component
"""

import json
import requests
import sys
from pathlib import Path
from typing import Dict, List, Tuple

OLLAMA_SERVER = "http://<NAS_IP>:8080"
CONFIG_PATH = Path(__file__).parent.parent.parent / ".continue" / "config.yaml"


def get_available_models() -> List[str]:
    """Get list of available models from Ollama server."""
    try:
        response = requests.get(f"{OLLAMA_SERVER}/api/tags", timeout=5)
        response.raise_for_status()
        data = response.json()
        return [model["name"] for model in data.get("models", [])]
    except Exception as e:
        print(f"❌ Error connecting to Ollama server: {e}")
        return []


def parse_config_models(config_path: Path) -> List[str]:
    """Extract model names from Continue config.yaml."""
    models = []
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Only extract models from uncommented sections
            in_comment = False
            for i, line in enumerate(lines):
                # Check if line starts a comment block
                if line.strip().startswith('#') and 'UNAVAILABLE' in line:
                    in_comment = True
                elif in_comment and not line.strip().startswith('#'):
                    in_comment = False

                # Skip commented lines and unavailable sections
                if line.strip().startswith('#') or in_comment:
                    continue

                # Extract model names from uncommented model: lines
                import re
                match = re.search(r'model:\s*([^\s#]+)', line)
                if match:
                    model = match.group(1).strip()
                    if model and not model.startswith('$'):
                        models.append(model)
    except Exception as e:
        print(f"❌ Error reading config: {e}")
    return models


def validate_models(available: List[str], configured: List[str]) -> Tuple[List[str], List[str]]:
    """Compare configured models against available models."""
    available_set = set(available)
    configured_set = set(configured)

    valid = list(configured_set & available_set)
    missing = list(configured_set - available_set)

    return valid, missing


def main():
    """Main validation function."""
    print("🔬 RR Model Validation - Rest, Roast, Repair")
    print("=" * 60)

    # REST: Get current state
    print("\n🛌 REST: Analyzing current state...")
    available_models = get_available_models()
    configured_models = parse_config_models(CONFIG_PATH)

    if not available_models:
        print("❌ Cannot connect to Ollama server. Exiting.")
        sys.exit(1)

    print(f"✓ Server accessible: {OLLAMA_SERVER}")
    print(f"✓ Available models: {len(available_models)}")
    print(f"✓ Configured models: {len(configured_models)}")

    # ROAST: Identify issues
    print("\n🔥 ROAST: Identifying issues...")
    valid, missing = validate_models(available_models, configured_models)

    print(f"\n✅ Valid models ({len(valid)}):")
    for model in sorted(valid):
        print(f"   ✓ {model}")

    if missing:
        print(f"\n❌ Missing models ({len(missing)}):")
        for model in sorted(missing):
            print(f"   ✗ {model}")

    # REPAIR: Recommendations
    print("\n🔧 REPAIR: Recommendations...")
    if missing:
        print(f"\n⚠️  {len(missing)} configured model(s) not available on server.")
        print("   Action: Pull missing models or remove from config.")
        print("\n   To pull models, run:")
        for model in missing:
            print(f"   ollama pull {model}")
        return 1
    else:
        print("✅ All configured models are available!")
        return 0


if __name__ == "__main__":

    sys.exit(main())