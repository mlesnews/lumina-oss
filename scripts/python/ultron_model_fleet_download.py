#!/usr/bin/env python3
"""
🤖 ULTRON Model Fleet Downloader

Downloads optimal models to NAS for the ULTRON cluster:
- MILLENNIUM-FALC (laptop RTX 5090 24GB)
- KAIJU (NAS)
- Iron Legion (future cluster nodes)

Models selected for:
- Trading/financial analysis
- Code generation
- General reasoning
- Fast inference
- Quality/speed tradeoffs

Azure AI Foundry Integration Ready
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import json
import logging
logger = logging.getLogger("ultron_model_fleet_download")


# Model fleet selection
ULTRON_MODEL_FLEET = [
    # Already downloaded
    {"name": "smollm:135m", "size": "91MB", "purpose": "Ultra-fast simple tasks", "downloaded": True},
    {"name": "mistral:latest", "size": "4.4GB", "purpose": "General reasoning 7B", "downloaded": True},
    {"name": "codellama:13b", "size": "7.4GB", "purpose": "Code generation", "downloaded": True},

    # New models to download
    {"name": "llama3.2:3b", "size": "2.0GB", "purpose": "Fast Llama for quick tasks", "downloaded": False},
    {"name": "llama3.2:latest", "size": "2.0GB", "purpose": "Latest Llama general model", "downloaded": False},
    {"name": "deepseek-coder:6.7b", "size": "3.8GB", "purpose": "Specialized coding model", "downloaded": False},
    {"name": "phi3:medium", "size": "7.9GB", "purpose": "Microsoft efficient reasoning", "downloaded": False},
    {"name": "qwen2.5:7b", "size": "4.7GB", "purpose": "Strong multilingual model", "downloaded": False},
    {"name": "gemma2:9b", "size": "5.4GB", "purpose": "Google's quality model", "downloaded": False},
    {"name": "codellama:7b", "size": "3.8GB", "purpose": "Smaller fast code model", "downloaded": False},
]

# VRAM requirements for simultaneous loading
VRAM_PROFILES = {
    "single_large": {
        "description": "One large model at a time",
        "models": ["codellama:13b", "phi3:medium", "gemma2:9b"],
        "vram_needed": "~10-12GB"
    },
    "dual_medium": {
        "description": "Two medium models simultaneously", 
        "models": ["mistral:latest", "deepseek-coder:6.7b"],
        "vram_needed": "~12GB"
    },
    "triple_small": {
        "description": "Three small models for fast switching",
        "models": ["smollm:135m", "llama3.2:3b", "codellama:7b"],
        "vram_needed": "~8GB"
    },
    "code_focused": {
        "description": "Coding-optimized combination",
        "models": ["codellama:13b", "smollm:135m"],
        "vram_needed": "~10GB"
    },
    "trading_analysis": {
        "description": "Trading and analysis focused",
        "models": ["mistral:latest", "qwen2.5:7b", "smollm:135m"],
        "vram_needed": "~12GB"
    }
}


def download_model(model_name: str) -> bool:
    """Download a model using Ollama"""
    print(f"📥 Downloading {model_name}...")
    try:
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=False,
            text=True,
            timeout=1800  # 30 min timeout
        )
        if result.returncode == 0:
            print(f"✅ {model_name} downloaded successfully")
            return True
        else:
            print(f"❌ {model_name} download failed")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {model_name} download timed out")
        return False
    except Exception as e:
        print(f"❌ Error downloading {model_name}: {e}")
        return False


def list_downloaded_models() -> List[str]:
    """List currently downloaded models"""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            return [line.split()[0] for line in lines if line.strip()]
    except:
        pass
    return []


def download_fleet(skip_existing: bool = True):
    """Download the full model fleet"""
    print("=" * 80)
    print("🤖 ULTRON MODEL FLEET DOWNLOADER")
    print("=" * 80)
    print()

    existing = list_downloaded_models()
    print(f"Currently downloaded: {len(existing)} models")
    for m in existing:
        print(f"  ✅ {m}")
    print()

    to_download = []
    for model in ULTRON_MODEL_FLEET:
        name = model["name"]
        # Check if already downloaded (match base name)
        base_name = name.split(":")[0]
        already_have = any(base_name in e for e in existing)

        if already_have and skip_existing:
            print(f"⏭️  Skipping {name} (already downloaded)")
        else:
            to_download.append(model)

    print()
    print(f"Models to download: {len(to_download)}")
    total_size = sum(float(m['size'].replace('GB','').replace('MB','')) 
                     for m in to_download if 'GB' in m['size'])
    print(f"Estimated total size: ~{total_size:.1f} GB")
    print()

    success_count = 0
    for model in to_download:
        if download_model(model["name"]):
            success_count += 1

    print()
    print("=" * 80)
    print(f"✅ Downloaded {success_count}/{len(to_download)} models")
    print("=" * 80)

    return success_count


def generate_azure_ai_foundry_config() -> Dict[str, Any]:
    """Generate Azure AI Foundry integration config"""
    config = {
        "azure_ai_foundry": {
            "enabled": True,
            "workspace": "lumina-ai-workspace",
            "resource_group": "lumina-rg",
            "endpoints": {
                "local_ollama": "http://localhost:11434",
                "kaiju_ollama": "http://<NAS_PRIMARY_IP>:11434",
            },
            "model_registry": {
                "local_models": ULTRON_MODEL_FLEET,
                "vram_profiles": VRAM_PROFILES,
            },
            "routing": {
                "default": "local_ollama",
                "fallback": "kaiju_ollama",
                "cost_optimization": True,
                "latency_priority": ["smollm:135m", "llama3.2:3b"],
                "quality_priority": ["codellama:13b", "phi3:medium", "gemma2:9b"],
            }
        },
        "ultron_cluster": {
            "millennium_falc": {
                "type": "laptop",
                "gpu": "RTX 5090",
                "vram": "24GB",
                "role": "primary_inference",
                "ollama_endpoint": "http://localhost:11434"
            },
            "kaiju": {
                "type": "nas",
                "role": "model_storage_and_backup_inference",
                "ollama_endpoint": "http://<NAS_PRIMARY_IP>:11434",
                "model_storage": "\\\\<NAS_PRIMARY_IP>\\backups\\ollama_models"
            },
            "iron_legion": {
                "type": "cluster",
                "nodes": [],
                "role": "distributed_inference",
                "status": "planned"
            }
        },
        "generated": datetime.now().isoformat()
    }
    return config


def main():
    try:
        import argparse

        parser = argparse.ArgumentParser(description="ULTRON Model Fleet Downloader")
        parser.add_argument("--download", action="store_true", help="Download all models")
        parser.add_argument("--list", action="store_true", help="List model fleet")
        parser.add_argument("--profiles", action="store_true", help="Show VRAM profiles")
        parser.add_argument("--config", action="store_true", help="Generate Azure AI Foundry config")

        args = parser.parse_args()

        if args.list:
            print("🤖 ULTRON MODEL FLEET")
            print("=" * 80)
            for model in ULTRON_MODEL_FLEET:
                status = "✅" if model.get("downloaded") else "📥"
                print(f"  {status} {model['name']:20} {model['size']:>8}  - {model['purpose']}")

        elif args.profiles:
            print("🎯 VRAM LOADING PROFILES")
            print("=" * 80)
            for name, profile in VRAM_PROFILES.items():
                print(f"\n  {name}:")
                print(f"    Description: {profile['description']}")
                print(f"    Models: {', '.join(profile['models'])}")
                print(f"    VRAM: {profile['vram_needed']}")

        elif args.config:
            config = generate_azure_ai_foundry_config()
            print(json.dumps(config, indent=2))

        elif args.download:
            download_fleet()

        else:
            # Default: show status
            print("🤖 ULTRON MODEL FLEET STATUS")
            print("=" * 80)
            existing = list_downloaded_models()
            print(f"Downloaded: {len(existing)}")
            print(f"Fleet size: {len(ULTRON_MODEL_FLEET)}")
            print("\nUse --download to pull remaining models")
            print("Use --list to see all models")
            print("Use --profiles to see VRAM configurations")
            print("Use --config to generate Azure AI Foundry config")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()