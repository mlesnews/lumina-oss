#!/usr/bin/env python3
"""
Download Peak Models to M Drive
Downloads the largest models compatible with RTX 5090 Mobile (24GB) and moves them to M drive

GPU: RTX 5090 Mobile (24GB GDDR7)
Optimization: 4-bit quantization (GGUF)
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import json
import logging
logger = logging.getLogger("download_peak_models_to_m_drive")


# RTX 5090 Mobile (24GB) compatible models with 4-bit quantization
PEAK_MODELS = [
    {
        "name": "qwen2.5:72b",
        "quantization": "Q4_K_M",  # 4-bit medium quantization
        "estimated_size_gb": 40,
        "vram_required_gb": 20,
        "description": "Largest model - 72B parameters, excellent quality",
        "priority": 1
    },
    {
        "name": "qwen2.5:32b",
        "quantization": "Q4_K_M",
        "estimated_size_gb": 18,
        "vram_required_gb": 16,
        "description": "Large model - 32B parameters, great quality",
        "priority": 2
    },
    {
        "name": "qwen2.5-coder:32b",
        "quantization": "Q4_K_M",
        "estimated_size_gb": 18,
        "vram_required_gb": 16,
        "description": "Large coding model - 32B parameters, specialized for code",
        "priority": 3
    },
    {
        "name": "qwen2.5:14b",
        "quantization": "Q4_K_M",
        "estimated_size_gb": 8,
        "vram_required_gb": 8,
        "description": "Medium model - 14B parameters, good balance",
        "priority": 4
    },
]

# M Drive paths (NAS)
M_DRIVE_PATHS = [
    Path("M:/Ollama/models"),
    Path("M:/ollama/models"),
    Path("M:/models/ollama"),
    Path("M:/Jarvis/Ollama/Models"),
    Path("M:/ai/models"),
]

# Local Ollama paths
LOCAL_OLLAMA_PATHS = [
    Path.home() / ".ollama" / "models",
    Path(os.environ.get("OLLAMA_MODELS", "")),
    Path("C:/Users/Public/.ollama/models"),
]


def find_m_drive() -> Optional[Path]:
    """Find M drive path"""
    for path in M_DRIVE_PATHS:
        if path.exists():
            print(f"✅ Found M drive at: {path}")
            return path

    # Try to find M drive root
    for drive in "MNO":
        test_path = Path(f"{drive}:/")
        if test_path.exists():
            print(f"✅ Found drive {drive}: at: {test_path}")
            # Create models directory structure
            models_path = test_path / "Ollama" / "models"
            models_path.mkdir(parents=True, exist_ok=True)
            return models_path

    print("⚠️  M drive not found. Trying NAS path...")
    # Try NAS path directly
    nas_paths = [
        Path("//<NAS_PRIMARY_IP>/volume1/Jarvis/Ollama/Models"),
        Path("//<NAS_PRIMARY_IP>/homes/mlesn/Ollama/models"),
    ]
    for path in nas_paths:
        try:
            if path.exists():
                print(f"✅ Found NAS path: {path}")
                return path
        except:
            pass

    return None


def find_local_ollama_models() -> Optional[Path]:
    try:
        """Find local Ollama models directory"""
        for path in LOCAL_OLLAMA_PATHS:
            if path and path.exists():
                print(f"✅ Found local Ollama models at: {path}")
                return path

        # Default location
        default_path = Path.home() / ".ollama" / "models"
        default_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Using default Ollama models path: {default_path}")
        return default_path


    except Exception as e:
        logger.error(f"Error in find_local_ollama_models: {e}", exc_info=True)
        raise
def check_ollama_installed() -> bool:
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"✅ Ollama installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        print("❌ Ollama not found. Please install Ollama first.")
        return False
    except Exception as e:
        print(f"⚠️  Error checking Ollama: {e}")
        return False
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
            models = []
            for line in lines:
                if line.strip():
                    model_name = line.split()[0]
                    models.append(model_name)
            return models
    except Exception as e:
        print(f"⚠️  Error listing models: {e}")
    return []


def download_model(model_name: str, quantization: Optional[str] = None) -> bool:
    """Download a model using IDM ONLY (no Ollama fallback)"""
    print(f"\n📥 Downloading {model_name}...")
    if quantization:
        print(f"   Quantization: {quantization}")

    # IDM is mandatory - no fallback
    try:
        from jarvis_ollama_idm_pull import OllamaIDMPuller
        idm_puller = OllamaIDMPuller(Path(__file__).parent.parent.parent)

        if not idm_puller.idm or not idm_puller.idm.is_available():
            print(f"   ❌ IDM not available - download aborted")
            print(f"   Please ensure Internet Download Manager is installed and running")
            return False

        print(f"   🚀 Using IDM for download...")
        result = idm_puller.pull_model_with_idm(
            model_name,
            endpoint="http://localhost:11434"
        )

        if result.get("success"):
            print(f"   ✅ {model_name} queued in IDM")
            print(f"   📊 Monitor download progress in IDM application")
            return True
        else:
            print(f"   ❌ {model_name} failed to queue in IDM: {result.get('error', 'unknown error')}")
            return False
    except ImportError as e:
        print(f"   ❌ IDM integration not available: {e}")
        print(f"   Please ensure IDM integration is properly configured")
        return False
    except Exception as e:
        print(f"   ❌ Error with IDM: {e}")
        return False

    # NO OLLAMA FALLBACK - IDM is required
    print(f"   ❌ Download aborted - IDM is required for all downloads")
    return False


def move_models_to_m_drive(local_path: Path, m_drive_path: Path) -> bool:
    """Move models from local to M drive"""
    print(f"\n📦 Moving models from {local_path} to {m_drive_path}...")

    if not local_path.exists():
        print(f"⚠️  Local path doesn't exist: {local_path}")
        return False

    if not m_drive_path.exists():
        print(f"📁 Creating M drive directory: {m_drive_path}")
        m_drive_path.mkdir(parents=True, exist_ok=True)

    try:
        # Copy models (blobs, manifests, etc.)
        items_to_copy = ["blobs", "manifests", "models"]
        copied = False

        for item_name in items_to_copy:
            source = local_path / item_name
            if source.exists():
                dest = m_drive_path / item_name
                print(f"   Copying {item_name}...")

                if dest.exists():
                    # Merge directories
                    if source.is_dir() and dest.is_dir():
                        for subitem in source.iterdir():
                            subdest = dest / subitem.name
                            if not subdest.exists():
                                if subitem.is_dir():
                                    shutil.copytree(subitem, subdest)
                                else:
                                    shutil.copy2(subitem, subdest)
                                copied = True
                else:
                    if source.is_dir():
                        shutil.copytree(source, dest)
                    else:
                        shutil.copy2(source, dest)
                    copied = True

        if copied:
            print(f"✅ Models copied to M drive")

            # Update Ollama to use M drive
            print(f"\n⚙️  To use M drive models, set OLLAMA_MODELS environment variable:")
            print(f"   setx OLLAMA_MODELS \"{m_drive_path}\"")
            print(f"   Or update Ollama config to point to: {m_drive_path}")
            return True
        else:
            print(f"⚠️  No models found to copy")
            return False

    except Exception as e:
        print(f"❌ Error moving models: {e}")
        return False


def configure_ollama_for_m_drive(m_drive_path: Path):
    """Configure Ollama to use M drive"""
    print(f"\n⚙️  Configuring Ollama to use M drive...")

    # Set environment variable
    try:
        subprocess.run(
            ["setx", "OLLAMA_MODELS", str(m_drive_path)],
            check=True
        )
        print(f"✅ Set OLLAMA_MODELS environment variable")
    except Exception as e:
        print(f"⚠️  Could not set environment variable: {e}")
        print(f"   Please manually set: OLLAMA_MODELS={m_drive_path}")

    # Create symlink if possible
    local_ollama = Path.home() / ".ollama" / "models"
    if local_ollama.exists() and not local_ollama.is_symlink():
        try:
            # Backup existing
            backup = local_ollama.with_suffix('.backup')
            if backup.exists():
                shutil.rmtree(backup)
            shutil.move(str(local_ollama), str(backup))

            # Create symlink (Windows requires admin)
            try:
                subprocess.run(
                    ["mklink", "/D", str(local_ollama), str(m_drive_path)],
                    shell=True,
                    check=True
                )
                print(f"✅ Created symlink: {local_ollama} -> {m_drive_path}")
            except:
                print(f"⚠️  Could not create symlink (may need admin). Using environment variable instead.")
                shutil.move(str(backup), str(local_ollama))
        except Exception as e:
            print(f"⚠️  Could not create symlink: {e}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Download Peak Models to M Drive",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all peak models
  python download_peak_models_to_m_drive.py --download

  # Download specific model
  python download_peak_models_to_m_drive.py --download --model qwen2.5:32b

  # Just move existing models to M drive
  python download_peak_models_to_m_drive.py --move-only

  # List available models
  python download_peak_models_to_m_drive.py --list
        """
    )
    parser.add_argument("--download", action="store_true", help="Download models")
    parser.add_argument("--move-only", action="store_true", help="Only move existing models to M drive")
    parser.add_argument("--model", help="Download specific model")
    parser.add_argument("--list", action="store_true", help="List peak models")
    parser.add_argument("--m-drive", help="Custom M drive path")

    args = parser.parse_args()

    print("=" * 80)
    print("🚀 PEAK MODEL DOWNLOADER - RTX 5090 Mobile (24GB)")
    print("=" * 80)
    print()

    # Check Ollama
    if not check_ollama_installed():
        print("\n❌ Please install Ollama first: https://ollama.ai")
        return 1

    # Find M drive
    if args.m_drive:
        m_drive_path = Path(args.m_drive)
    else:
        m_drive_path = find_m_drive()

    if not m_drive_path:
        print("\n❌ M drive not found. Please specify with --m-drive")
        return 1

    # Find local Ollama
    local_ollama_path = find_local_ollama_models()

    if args.list:
        print("\n📋 PEAK MODELS (RTX 5090 Mobile 24GB compatible):")
        print("-" * 80)
        for model in sorted(PEAK_MODELS, key=lambda x: x["priority"]):
            print(f"  {model['name']:25} {model['estimated_size_gb']:>6} GB  - {model['description']}")
        return 0

    if args.move_only:
        # Just move existing models
        if move_models_to_m_drive(local_ollama_path, m_drive_path):
            configure_ollama_for_m_drive(m_drive_path)
            print("\n✅ Models moved to M drive")
            return 0
        else:
            print("\n❌ Failed to move models")
            return 1

    if args.download:
        # Download models
        existing_models = list_downloaded_models()
        print(f"\n📦 Currently downloaded: {len(existing_models)} models")

        models_to_download = []
        if args.model:
            # Download specific model
            models_to_download = [m for m in PEAK_MODELS if m["name"] == args.model]
            if not models_to_download:
                print(f"❌ Model not found: {args.model}")
                return 1
        else:
            # Download all peak models
            models_to_download = sorted(PEAK_MODELS, key=lambda x: x["priority"])

        print(f"\n📥 Models to download: {len(models_to_download)}")
        total_size = sum(m["estimated_size_gb"] for m in models_to_download)
        print(f"   Estimated total size: ~{total_size:.1f} GB")
        print()

        success_count = 0
        for model in models_to_download:
            model_name = model["name"]

            # Check if already downloaded
            if any(model_name.split(":")[0] in existing for existing in existing_models):
                print(f"⏭️  Skipping {model_name} (already downloaded)")
                continue

            if download_model(model_name, model.get("quantization")):
                success_count += 1

        print("\n" + "=" * 80)
        print(f"✅ Downloaded {success_count}/{len(models_to_download)} models")
        print("=" * 80)

        # Move to M drive
        print("\n📦 Moving models to M drive...")
        if move_models_to_m_drive(local_ollama_path, m_drive_path):
            configure_ollama_for_m_drive(m_drive_path)
            print("\n✅ All models downloaded and moved to M drive!")
            print("\n💡 Next steps:")
            print("   1. Restart Ollama service")
            print("   2. Verify models: ollama list")
            print("   3. Test model: ollama run qwen2.5:32b")
            return 0
        else:
            print("\n⚠️  Models downloaded but not moved to M drive")
            return 1

    # Default: show status
    print("💡 Usage:")
    print("   --download      Download all peak models")
    print("   --move-only     Move existing models to M drive")
    print("   --list          List available peak models")
    print("   --model NAME    Download specific model")
    return 0


if __name__ == "__main__":

    sys.exit(main())