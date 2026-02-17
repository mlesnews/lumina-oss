#!/usr/bin/env python3
"""
Configure Ollama for Network Access

Makes Ollama accessible from network (not just localhost).
"""

import subprocess
import requests
import json
from pathlib import Path
import os

def configure_ollama_network():
    """Configure Ollama to accept network connections"""
    print("🔧 Configuring Ollama for network access...")

    # Method 1: Set OLLAMA_HOST environment variable
    print("   Method 1: Setting OLLAMA_HOST=0.0.0.0...")

    # Windows: Set system environment variable
    try:
        subprocess.run(
            ["setx", "OLLAMA_HOST", "0.0.0.0"],
            check=True,
            timeout=10
        )
        print("   ✅ OLLAMA_HOST set to 0.0.0.0")
    except Exception as e:
        print(f"   ⚠️  Could not set environment variable: {e}")

    # Method 2: Update Ollama config file
    ollama_config_dir = Path.home() / ".ollama"
    ollama_config_file = ollama_config_dir / "config.json"

    if ollama_config_dir.exists():
        config = {}
        if ollama_config_file.exists():
            try:
                with open(ollama_config_file, 'r') as f:
                    config = json.load(f)
            except:
                pass

        config["OLLAMA_HOST"] = "0.0.0.0"
        config["OLLAMA_ORIGINS"] = "*"

        try:
            with open(ollama_config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"   ✅ Updated config: {ollama_config_file}")
        except Exception as e:
            print(f"   ⚠️  Could not update config: {e}")

    # Method 3: Restart Ollama service
    print("   Method 3: Restarting Ollama...")
    try:
        # Check if Ollama is running
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("   ✅ Ollama is running")
            print("   💡 Restart Ollama Desktop or service to apply network settings")
    except:
        print("   ⚠️  Ollama not running - start it after configuration")

    print()
    print("✅ Configuration complete!")
    print("   Ollama will be accessible at: http://<your-ip>:11434")
    print("   Restart Ollama for changes to take effect")

if __name__ == "__main__":
    configure_ollama_network()
